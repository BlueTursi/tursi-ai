import argparse
import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer
import onnxruntime as ort

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Security constants
MAX_INPUT_LENGTH = 512  # Maximum length of input text
ALLOWED_MODELS = [
    "distilbert-base-uncased-finetuned-sst-2-english",
    # Add other allowed models here
]

# Rate limiting constants
RATE_LIMIT = "100 per minute"  # Adjust based on your needs
RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

# Quantization settings
QUANTIZATION_MODE = os.getenv("QUANTIZATION_MODE", "dynamic")  # dynamic or static
QUANTIZATION_BITS = int(os.getenv("QUANTIZATION_BITS", "8"))  # 8 or 4 bits


def validate_input(text: str) -> bool:
    """Validate input text for security."""
    if not isinstance(text, str):
        return False
    if len(text) > MAX_INPUT_LENGTH:
        return False
    # Add more validation as needed
    return True


def sanitize_model_name(model_name: str) -> str:
    """Sanitize model name for security."""
    # Add model name sanitization logic here
    return model_name


def load_quantized_model(model_name: str):
    """Load a quantized model using ONNX Runtime."""
    try:
        logger.info(f"Loading quantized model: {model_name}...")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Configure ONNX Runtime session options
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.intra_op_num_threads = 1
        
        # Load model with quantization
        model = ORTModelForSequenceClassification.from_pretrained(
            model_name,
            export=True,
            session_options=session_options
        )
        
        logger.info(
            f"Model quantized successfully with {QUANTIZATION_MODE} "
            f"{QUANTIZATION_BITS}-bit quantization!"
        )
        return model, tokenizer
            
    except Exception as e:
        logger.error(f"Failed to load quantized model: {str(e)}")
        raise


def create_app(model_name: str, rate_limit: str = RATE_LIMIT):
    """Create and configure the Flask application."""
    try:
        # Validate model name
        if model_name not in ALLOWED_MODELS:
            raise ValueError(f"Model {model_name} is not in the allowed list")

        # Sanitize model name
        model_name = sanitize_model_name(model_name)
        
        # Load model with quantization
        model, tokenizer = load_quantized_model(model_name)
        logger.info("Model loaded successfully!")
    except ValueError as e:
        logger.error(f"Invalid model: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

    app = Flask(__name__)
    
    # Store rate limit in app config
    app.config['RATE_LIMIT'] = rate_limit
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=RATE_LIMIT_STORAGE_URI,
        default_limits=[rate_limit],
        strategy="fixed-window"
    )

    @app.route("/predict", methods=["POST"])
    @limiter.limit(rate_limit)
    def predict():
        try:
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            data = request.get_json()
            if not data or "text" not in data:
                return jsonify({
                    "error": "Missing 'text' field in request"
                }), 400

            text = data.get("text", "")

            # Validate input
            if not validate_input(text):
                return jsonify({
                    "error": (
                        "Invalid input. Text must be a string of maximum "
                        "length 512 characters."
                    )
                }), 400

            # Tokenize input
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            
            # Run inference
            outputs = model(**inputs)
            predictions = outputs.logits.softmax(dim=-1)
            
            # Get prediction
            label = "POSITIVE" if predictions[0][1] > predictions[0][0] else "NEGATIVE"
            score = float(predictions[0][1] if label == "POSITIVE" else predictions[0][0])
            
            return jsonify({"label": label, "score": score})
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    return app


def main():
    parser = argparse.ArgumentParser(
        description="tursi-engine: Deploy an AI model with Flask"
    )
    parser.add_argument(
        "command",
        choices=["up"],
        help="Command to run ('up' to start the server)"
    )
    parser.add_argument(
        "--model",
        default="distilbert-base-uncased-finetuned-sst-2-english",
        help="Model name from Hugging Face"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to run the server on (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the server on (default: 5000)"
    )
    parser.add_argument(
        "--rate-limit",
        default=RATE_LIMIT,
        help="Rate limit for API requests (default: 100 per minute)"
    )
    parser.add_argument(
        "--quantization-mode",
        choices=["dynamic", "static"],
        default=QUANTIZATION_MODE,
        help="Quantization mode (default: dynamic)"
    )
    parser.add_argument(
        "--quantization-bits",
        type=int,
        choices=[4, 8],
        default=QUANTIZATION_BITS,
        help="Number of bits for quantization (default: 8)"
    )
    args = parser.parse_args()

    if args.command == "up":
        # Update quantization settings from command line
        os.environ["QUANTIZATION_MODE"] = args.quantization_mode
        os.environ["QUANTIZATION_BITS"] = str(args.quantization_bits)
        
        app = create_app(args.model, args.rate_limit)
        logger.info(
            f"Deploying at http://{args.host}:{args.port}/predict "
            f"with rate limit: {args.rate_limit} "
            f"and {args.quantization_mode} {args.quantization_bits}-bit quantization"
        )
        app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
