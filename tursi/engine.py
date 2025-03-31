import argparse
import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from transformers import pipeline

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


def create_app(model_name: str, rate_limit: str = RATE_LIMIT):
    """Create and configure the Flask application."""
    try:
        # Sanitize model name
        model_name = sanitize_model_name(model_name)
        logger.info(f"Loading model: {model_name}...")
        
        # Load model with security settings
        model = pipeline(
            "text-classification",
            model=model_name,
            device=-1  # Use CPU only for better security
        )
        logger.info("Model loaded successfully!")
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
                return jsonify({"error": "Missing 'text' field in request"}), 400
                
            text = data.get("text", "")
            
            # Validate input
            if not validate_input(text):
                return jsonify({
                    "error": (
                        "Invalid input. Text must be a string of maximum length "
                        "512 characters."
                    )
                }), 400
            
            # Run inference
            result = model(text)
            return jsonify(result[0])
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
    args = parser.parse_args()

    if args.command == "up":
        app = create_app(args.model, args.rate_limit)
        logger.info(
            f"Deploying at http://{args.host}:{args.port}/predict "
            f"with rate limit: {args.rate_limit}"
        )
        app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
