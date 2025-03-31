import argparse
import os
import signal
import sys
import time
from multiprocessing import Process
from transformers import pipeline
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import logging
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

PID_FILE = "tursi_engine.pid"

def validate_input(text: str) -> bool:
    """Validate input text for security."""
    if not isinstance(text, str):
        return False
    if len(text) > MAX_INPUT_LENGTH:
        return False
    # Add more validation as needed
    return True

def sanitize_model_name(model_name: str) -> str:
    """Sanitize and validate model name."""
    if model_name not in ALLOWED_MODELS:
        raise ValueError(f"Model {model_name} is not in the allowed list")
    return model_name

def run_server(model_name, host, port):
    """Run the Flask server in a separate process."""
    # Redirect stdout/stderr to suppress output in parent terminal
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        sys.stderr = devnull
        print(f"Loading model: {model_name}...")
        try:
            model = pipeline("text-classification", model=model_name)
            print("Model loaded!")
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            sys.exit(1)

        app = Flask(__name__)
        
        # Initialize rate limiter
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage_uri=RATE_LIMIT_STORAGE_URI,
            default_limits=[RATE_LIMIT],
            strategy="fixed-window"
        )

        @app.route("/predict", methods=["POST"])
        @limiter.limit(RATE_LIMIT)
        def predict():
            try:
                if not request.is_json:
                    return jsonify({"error": "Request must be JSON"}), 400
                data = request.get_json()
                text = data.get("text", "")
                if not text:
                    return jsonify({"error": "Missing 'text' in payload"}), 400
                result = model(text)
                return jsonify(result[0])
            except Exception as e:
                logger.error(f"Error during prediction: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        print(f"Deploying at http://{host}:{port}/predict")
        # Disable debug mode in production
        app.run(host=host, port=port, debug=False)

def is_server_running(pid):
    """Check if the process with given PID is still alive."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

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
        try:
            # Sanitize model name
            model_name = sanitize_model_name(args.model)
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
            return

        app = Flask(__name__)
        
        # Initialize rate limiter
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage_uri=RATE_LIMIT_STORAGE_URI,
            default_limits=[args.rate_limit],
            strategy="fixed-window"
        )

        @app.route("/predict", methods=["POST"])
        @limiter.limit(args.rate_limit)
        def predict():
            try:
                if not request.is_json:
                    return jsonify({"error": "Request must be JSON"}), 400
                
                data = request.get_json()
                text = data.get("text", "")
                
                # Validate input
                if not validate_input(text):
                    return jsonify({
                        "error": "Invalid input. Text must be a string of maximum length 512 characters."
                    }), 400
                
                # Run inference
                result = model(text)
                return jsonify(result[0])
            except Exception as e:
                logger.error(f"Error during prediction: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        logger.info(f"Deploying at http://{args.host}:{args.port}/predict with rate limit: {args.rate_limit}")
        # Disable debug mode in production
        app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
