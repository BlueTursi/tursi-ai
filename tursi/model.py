"""Model management and deployment for Tursi."""

import os
import logging
import torch
from typing import Dict, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import Flask, request, jsonify
from werkzeug.serving import make_server
import threading

logger = logging.getLogger(__name__)


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
        return jsonify({"status": "healthy", "model": self.model_name}), 200


class ModelManager:
    """Manager for model deployments."""

    def __init__(self):
        """Initialize the model manager."""
        self.models: Dict[str, Dict] = {}  # model_name -> {model, tokenizer, server}
        self.servers: Dict[int, Dict] = (
            {}
        )  # port -> {thread, server_instance, stop_event}

    def load_model(
        self,
        model_name: str,
        quantization: Optional[str] = None,
        bits: Optional[int] = None,
    ) -> tuple:
        """Load a model from Hugging Face.

        Args:
            model_name: Name/path of the model on Hugging Face
            quantization: Quantization mode ('dynamic' or 'static')
            bits: Number of bits for quantization (4 or 8)

        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            logger.info(f"Loading model {model_name}")

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Configure quantization
            if quantization and bits:
                if quantization not in ["dynamic", "static"]:
                    raise ValueError("Quantization must be 'dynamic' or 'static'")
                if bits not in [4, 8]:
                    raise ValueError("Bits must be 4 or 8")

                from transformers import BitsAndBytesConfig

                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=(bits == 4),
                    load_in_8bit=(bits == 8),
                    bnb_4bit_quant_type="nf4" if bits == 4 else None,
                )

                # Load model with quantization
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    device_map="auto",
                )
            else:
                # Load model without quantization
                model = AutoModelForCausalLM.from_pretrained(model_name)
                if torch.cuda.is_available():
                    model = model.to("cuda")

            return model, tokenizer

        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise

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
        """
        try:
            # Check if port is already in use
            if port in self.servers:
                raise ValueError(f"Port {port} is already in use")

            # Load model if not already loaded
            if model_name not in self.models:
                model, tokenizer = self.load_model(model_name, quantization, bits)
                self.models[model_name] = {"model": model, "tokenizer": tokenizer}

            # Create server
            server = ModelServer(
                model_name=model_name,
                model=self.models[model_name]["model"],
                tokenizer=self.models[model_name]["tokenizer"],
                rate_limit=rate_limit,
            )

            # Create stop event
            stop_event = threading.Event()

            # Create and start server thread
            server_instance = make_server(host, port, server.app)
            server_thread = threading.Thread(
                target=self._run_server, args=(server_instance, stop_event)
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
        """
        if port not in self.servers:
            raise ValueError(f"No deployment found on port {port}")

        try:
            server_info = self.servers[port]

            # Signal server to stop
            server_info["stop_event"].set()
            server_info["server"].shutdown()

            # Wait for thread to finish
            server_info["thread"].join(timeout=5)

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

        def shutdown_check():
            while not stop_event.is_set():
                stop_event.wait(1)
            server.shutdown()

        # Start shutdown check thread
        threading.Thread(target=shutdown_check, daemon=True).start()

        # Run server
        server.serve_forever()

    def cleanup(self) -> None:
        """Clean up all model deployments."""
        # Stop all servers
        for port in list(self.servers.keys()):
            try:
                self.stop_model(port)
            except Exception as e:
                logger.error(f"Error stopping model on port {port}: {e}")

        # Clear models
        self.models.clear()
        logger.info("Cleaned up all model deployments")
