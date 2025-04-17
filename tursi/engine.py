import argparse
import os
import logging
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import onnxruntime as ort


class TursiEngine:
    """Main engine class for Tursi AI model deployment."""

    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Load environment variables
        load_dotenv()

        # Security constants
        self.MAX_INPUT_LENGTH = 512  # Maximum length of input text
        self.ALLOWED_MODELS = [
            "distilbert-base-uncased-finetuned-sst-2-english",
            # Add other allowed models here
        ]

        # Rate limiting constants
        self.RATE_LIMIT = "100 per minute"  # Adjust based on your needs
        self.RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

        # Quantization settings
        self.QUANTIZATION_MODE = os.getenv(
            "QUANTIZATION_MODE", "dynamic"
        )  # dynamic or static
        self.QUANTIZATION_BITS = int(os.getenv("QUANTIZATION_BITS", "8"))  # 8 or 4 bits

        # Model storage
        self.MODEL_CACHE_DIR = Path.home() / ".tursi" / "models"
        self.setup_model_cache()

    def setup_model_cache(self):
        """Create model cache directory if it doesn't exist."""
        self.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Model cache directory: {self.MODEL_CACHE_DIR}")

    def validate_input(self, text: str) -> bool:
        """Validate input text for security."""
        if not isinstance(text, str):
            return False
        if len(text) > self.MAX_INPUT_LENGTH:
            return False
        # Add more validation as needed
        return True

    def sanitize_model_name(self, model_name: str) -> str:
        """Sanitize model name for security."""
        # Remove any path traversal attempts
        return os.path.basename(model_name)

    def check_model_compatibility(self, model_name: str) -> bool:
        """Check if the model is compatible with our system."""
        try:
            config = AutoConfig.from_pretrained(model_name)
            # Check if model architecture is supported
            supported_architectures = ["DistilBert", "Bert", "RoBERTa", "GPT2"]
            return any(
                arch.lower() in config.architectures[0].lower()
                for arch in supported_architectures
            )
        except Exception as e:
            self.logger.error(f"Error checking model compatibility: {str(e)}")
            return False

    def load_quantized_model(self, model_name: str):
        """Load a quantized model using ONNX Runtime."""
        try:
            self.logger.info(f"Loading quantized model: {model_name}...")

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name, cache_dir=self.MODEL_CACHE_DIR
            )

            # Configure ONNX Runtime session options
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            )
            session_options.intra_op_num_threads = 1

            # Load model with quantization
            model = ORTModelForSequenceClassification.from_pretrained(
                model_name,
                export=True,
                session_options=session_options,
                cache_dir=self.MODEL_CACHE_DIR,
            )

            self.logger.info(
                f"Model quantized successfully with {self.QUANTIZATION_MODE} "
                f"{self.QUANTIZATION_BITS}-bit quantization!"
            )
            return model, tokenizer

        except Exception as e:
            self.logger.error(f"Failed to load quantized model: {str(e)}")
            raise

    def download_model(self, model_name: str) -> bool:
        """Download model and tokenizer files."""
        try:
            self.logger.info(f"Downloading model: {model_name}")
            AutoTokenizer.from_pretrained(model_name, cache_dir=self.MODEL_CACHE_DIR)
            AutoConfig.from_pretrained(model_name, cache_dir=self.MODEL_CACHE_DIR)
            return True
        except Exception as e:
            self.logger.error(f"Failed to download model: {str(e)}")
            return False

    def create_app(self, model_name: str, rate_limit: str = None):
        """Create and configure the Flask application."""
        if rate_limit is None:
            rate_limit = self.RATE_LIMIT

        try:
            # Validate model name
            if model_name not in self.ALLOWED_MODELS:
                raise ValueError(f"Model {model_name} is not in the allowed list")

            # Sanitize model name
            model_name = self.sanitize_model_name(model_name)

            # Load model with quantization
            model, tokenizer = self.load_quantized_model(model_name)
            self.logger.info("Model loaded successfully!")
        except ValueError as e:
            self.logger.error(f"Invalid model: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise

        app = Flask(__name__)

        # Store rate limit in app config
        app.config["RATE_LIMIT"] = rate_limit

        # Initialize rate limiter
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage_uri=self.RATE_LIMIT_STORAGE_URI,
            default_limits=[rate_limit],
            strategy="fixed-window",
        )

        @app.route("/predict", methods=["POST"])
        @limiter.limit(rate_limit)
        def predict():
            try:
                if not request.is_json:
                    return jsonify({"error": "Request must be JSON"}), 400

                data = request.get_json()
                if not data or "text" not in data:
                    return jsonify({"error": "Missing 'text' field in request"}), 400

                text = data.get("text", "")

                # Validate input
                if not self.validate_input(text):
                    return (
                        jsonify(
                            {
                                "error": (
                                    "Invalid input. Text must be a string of maximum "
                                    "length 512 characters."
                                )
                            }
                        ),
                        400,
                    )

                # Tokenize input
                inputs = tokenizer(
                    text, return_tensors="pt", padding=True, truncation=True
                )

                # Run inference
                outputs = model(**inputs)
                predictions = outputs.logits.softmax(dim=-1)

                # Get prediction
                label = (
                    "POSITIVE" if predictions[0][1] > predictions[0][0] else "NEGATIVE"
                )
                score = float(
                    predictions[0][1] if label == "POSITIVE" else predictions[0][0]
                )

                return jsonify({"label": label, "score": score})
            except Exception as e:
                self.logger.error(f"Error during prediction: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify(
                {
                    "status": "healthy",
                    "model": model_name,
                    "quantization": {
                        "mode": self.QUANTIZATION_MODE,
                        "bits": self.QUANTIZATION_BITS,
                    },
                }
            )

        return app


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Tursi AI Model Deployment")
    parser.add_argument("--model", type=str, required=True, help="Model name to deploy")
    parser.add_argument(
        "--rate-limit", type=str, help="Rate limit (e.g., '100 per minute')"
    )
    args = parser.parse_args()

    try:
        engine = TursiEngine()
        app = engine.create_app(args.model, args.rate_limit)
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
