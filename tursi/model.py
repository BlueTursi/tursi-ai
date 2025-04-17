"""Model management and deployment for Tursi."""

import os
import logging
import threading
from typing import Dict, Optional, Any, TypeVar
from dataclasses import dataclass
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)
from flask import Flask, request, jsonify
from werkzeug.serving import make_server
import time

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ModelConfig:
    """Configuration for model deployment."""

    model_name: str
    quantization: Optional[str] = None
    bits: Optional[int] = None
    rate_limit: Optional[str] = None
    device: str = "auto"

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.quantization and self.quantization not in ["dynamic", "static"]:
            raise ValueError("Quantization must be 'dynamic' or 'static'")
        if self.bits and self.bits not in [4, 8]:
            raise ValueError("Bits must be 4 or 8")
        if self.device not in ["auto", "cpu", "cuda"]:
            raise ValueError("Device must be 'auto', 'cpu', or 'cuda'")


@dataclass
class ModelInfo:
    """Information about a loaded model."""

    model: PreTrainedModel
    tokenizer: PreTrainedTokenizer
    config: ModelConfig
    deployment_count: int = 0


class ModelServer:
    """Flask server for model inference."""

    def __init__(
        self, model_name: str, model, tokenizer, rate_limit: Optional[str] = None
    ):
        """Initialize model server.

        Args:
            model_name: Name of the model being served
            model: The loaded model instance
            tokenizer: The model's tokenizer
            rate_limit: Optional rate limit string (e.g., "100/minute")
        """
        self.model_name = model_name
        self.model = model
        self.tokenizer = tokenizer
        self.rate_limit = rate_limit

        self.app = Flask(__name__)
        self._setup_routes()

        if rate_limit:
            from flask_limiter import Limiter
            from flask_limiter.util import get_remote_address

            self.limiter = Limiter(
                app=self.app, key_func=get_remote_address, default_limits=[rate_limit]
            )

    def _setup_routes(self):
        """Configure API routes."""
        self.app.route("/v1/generate", methods=["POST"])(self.generate)
        self.app.route("/v1/health", methods=["GET"])(self.health_check)

    def generate(self):
        """Generate text from the model."""
        try:
            data = request.get_json()
            if not data or "prompt" not in data:
                return jsonify({"error": "Missing prompt in request"}), 400

            prompt = data["prompt"]
            max_length = data.get("max_length", 100)
            temperature = data.get("temperature", 0.7)

            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    temperature=temperature,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            return jsonify({"generated_text": generated_text}), 200

        except Exception as e:
            logger.error(f"Error in generate: {e}")
            return jsonify({"error": str(e)}), 500

    def health_check(self):
        """Health check endpoint."""
        # Add more checks here if needed (e.g., model responsiveness)
        return (
            jsonify(
                {
                    "status": "healthy",
                    "model": self.model_name,
                    "message": "Server is running and model is loaded",
                }
            ),
            200,
        )


class ModelManager:
    """Manager for model deployments.

    This class follows the singleton pattern to ensure only one instance
    manages all models. It handles model lifecycle including loading,
    deployment, and cleanup.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "ModelManager":
        """Create or return the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the model manager.

        This will only run once due to the singleton pattern.
        """
        if not hasattr(self, "initialized"):
            self.models: Dict[str, ModelInfo] = {}
            self.servers: Dict[int, Dict[str, Any]] = {}
            self.initialized = True
            logger.info("ModelManager initialized")

    @classmethod
    def get_instance(cls) -> "ModelManager":
        """Get the singleton instance of ModelManager."""
        return cls()

    def register_model(self, config: ModelConfig) -> None:
        """Register a model configuration for later use.

        Args:
            config: Model configuration to register

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            config.validate()
            if config.model_name not in self.models:
                logger.info(f"Registering model configuration: {config.model_name}")
                self.models[config.model_name] = (
                    None  # Will be loaded on first deployment
                )
            else:
                logger.warning(f"Model {config.model_name} already registered")
        except Exception as e:
            logger.error(f"Error registering model {config.model_name}: {e}")
            raise

    def load_model(self, config: ModelConfig) -> ModelInfo:
        """Load a model from Hugging Face.

        Args:
            config: Configuration for model loading

        Returns:
            ModelInfo containing the loaded model and tokenizer

        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If model loading fails
        """
        start_time = time.time()
        logger.info(f"Starting model loading for {config.model_name}")
        try:
            config.validate()

            logger.debug(f"Loading tokenizer for {config.model_name}")
            tokenizer = AutoTokenizer.from_pretrained(config.model_name)
            logger.debug(f"Tokenizer loaded for {config.model_name}")

            model_kwargs = {}
            if config.quantization and config.bits:
                try:
                    from transformers import BitsAndBytesConfig
                except ImportError as e:
                    logger.error(
                        "BitsAndBytesConfig not found. Please install bitsandbytes: pip install bitsandbytes"
                    )
                    raise RuntimeError(
                        "Quantization requires bitsandbytes library"
                    ) from e

                logger.info(
                    f"Configuring {config.bits}-bit quantization ({config.quantization}) for {config.model_name}"
                )
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=(config.bits == 4),
                    load_in_8bit=(config.bits == 8),
                    bnb_4bit_quant_type="nf4" if config.bits == 4 else None,
                )

            # Determine device
            effective_device = config.device
            if effective_device == "auto":
                if torch.cuda.is_available():
                    effective_device = "cuda"
                elif torch.backends.mps.is_available():
                    effective_device = "mps"
                else:
                    effective_device = "cpu"
                logger.info(f"Auto device selection: Chose {effective_device}")

            if effective_device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available, falling back to CPU")
                effective_device = "cpu"
            elif effective_device == "mps" and not torch.backends.mps.is_available():
                logger.warning("MPS requested but not available, falling back to CPU")
                effective_device = "cpu"

            logger.info(
                f"Loading model {config.model_name} onto device: {effective_device}"
            )
            model = AutoModelForCausalLM.from_pretrained(
                config.model_name,
                device_map=(
                    "auto" if effective_device in ["cuda", "mps"] else None
                ),  # device_map only works for multi-GPU/MPS
                **model_kwargs,
            )

            # Explicitly move to device if not using device_map
            if effective_device == "cpu":
                model = model.to(effective_device)

            # Log memory usage (requires psutil)
            try:
                import psutil

                process = psutil.Process(os.getpid())
                mem_info = process.memory_info()
                logger.info(
                    f"Model {config.model_name} loaded. Current memory usage: {mem_info.rss / (1024 * 1024):.2f} MB"
                )
            except ImportError:
                logger.warning("psutil not installed, cannot report memory usage.")
            except Exception as mem_e:
                logger.warning(f"Could not get memory usage: {mem_e}")

            end_time = time.time()
            logger.info(
                f"Model {config.model_name} loaded successfully in {end_time - start_time:.2f} seconds"
            )
            return ModelInfo(model=model, tokenizer=tokenizer, config=config)

        except ValueError as ve:
            logger.error(f"Configuration error loading model {config.model_name}: {ve}")
            raise
        except ImportError as ie:
            logger.error(f"Import error during model loading: {ie}")
            raise RuntimeError(f"Missing dependency: {str(ie)}")
        except Exception as e:
            logger.error(f"Unexpected error loading model {config.model_name}: {e}")
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def deploy_model(
        self,
        model_name: str,
        host: str,
        port: int,
        quantization: Optional[str] = None,
        bits: Optional[int] = None,
        rate_limit: Optional[str] = None,
    ) -> None:
        """Deploy a model for inference.

        Args:
            model_name: Name/path of the model on Hugging Face
            host: Host address to bind to
            port: Port number to listen on
            quantization: Optional quantization mode
            bits: Optional number of bits for quantization
            rate_limit: Optional rate limit string

        Raises:
            ValueError: If port is in use or configuration is invalid
            RuntimeError: If deployment fails
        """
        try:
            # Check if port is already in use
            if port in self.servers:
                raise ValueError(f"Port {port} is already in use")

            # Create and validate config
            config = ModelConfig(
                model_name=model_name,
                quantization=quantization,
                bits=bits,
                rate_limit=rate_limit,
            )
            config.validate()

            # Load or get existing model
            if model_name not in self.models or self.models[model_name] is None:
                self.models[model_name] = self.load_model(config)

            model_info = self.models[model_name]
            model_info.deployment_count += 1

            # Create server
            server = ModelServer(
                model_name=model_name,
                model=model_info.model,
                tokenizer=model_info.tokenizer,
                rate_limit=rate_limit,
            )

            # Create stop event and server thread
            stop_event = threading.Event()
            server_instance = make_server(host, port, server.app)
            server_thread = threading.Thread(
                target=self._run_server,
                args=(server_instance, stop_event),
                name=f"ModelServer-{model_name}-{port}",
            )
            server_thread.daemon = True
            server_thread.start()

            # Store server info
            self.servers[port] = {
                "thread": server_thread,
                "server": server_instance,
                "stop_event": stop_event,
                "model_name": model_name,
            }

            logger.info(f"Model {model_name} deployed on {host}:{port}")

        except Exception as e:
            logger.error(f"Error deploying model {model_name}: {e}")
            raise

    def stop_model(self, port: int) -> None:
        """Stop a deployed model.

        Args:
            port: Port number of the deployment to stop

        Raises:
            ValueError: If no deployment found on port
            RuntimeError: If stopping fails
        """
        if port not in self.servers:
            raise ValueError(f"No deployment found on port {port}")

        try:
            server_info = self.servers[port]
            model_name = server_info["model_name"]

            # Signal server to stop
            server_info["stop_event"].set()
            server_info["server"].shutdown()

            # Wait for thread to finish
            server_info["thread"].join(timeout=5)
            if server_info["thread"].is_alive():
                logger.warning(f"Server thread on port {port} did not stop gracefully")

            # Update deployment count and cleanup if needed
            model_info = self.models[model_name]
            model_info.deployment_count -= 1

            # If no more deployments, unload model
            if model_info.deployment_count == 0:
                logger.info(f"No more deployments for {model_name}, unloading model")
                self.models[model_name] = None

            # Remove server info
            del self.servers[port]

            logger.info(f"Stopped model deployment on port {port}")

        except Exception as e:
            logger.error(f"Error stopping model on port {port}: {e}")
            raise

    def _run_server(self, server: make_server, stop_event: threading.Event) -> None:
        """Run the server in a separate thread.

        Args:
            server: Server instance to run
            stop_event: Event to signal server shutdown
        """

        def shutdown_check() -> None:
            """Check if server should shut down."""
            if stop_event.is_set():
                server.shutdown()

        # Add shutdown check to server
        server.service_actions = shutdown_check
        server.serve_forever()

    def cleanup(self) -> None:
        """Clean up all resources.

        This should be called when shutting down the application.
        """
        logger.info("Starting ModelManager cleanup")

        # Stop all servers
        for port in list(self.servers.keys()):
            try:
                self.stop_model(port)
            except Exception as e:
                logger.error(f"Error stopping model on port {port} during cleanup: {e}")

        # Clear all models
        self.models.clear()
        self.servers.clear()

        logger.info("ModelManager cleanup complete")

    def get_deployment_status(self) -> Dict[int, Dict[str, Any]]:
        """Get the status of all current model deployments.

        Returns:
            Dictionary mapping port numbers to deployment details.
        """
        status = {}
        for port, server_info in self.servers.items():
            model_info = self.models.get(server_info["model_name"])
            status[port] = {
                "model_name": server_info["model_name"],
                "host": server_info["server"].host,
                "port": server_info["server"].port,
                "thread_status": (
                    "alive" if server_info["thread"].is_alive() else "stopped"
                ),
                "quantization": model_info.config.quantization if model_info else "N/A",
                "bits": model_info.config.bits if model_info else "N/A",
                "rate_limit": model_info.config.rate_limit if model_info else "N/A",
                "device": model_info.config.device if model_info else "N/A",
            }
        return status
