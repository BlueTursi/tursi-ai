import argparse
import os
import signal
import sys
import time
from multiprocessing import Process
from transformers import pipeline
from flask import Flask, request, jsonify

PID_FILE = "tursi_engine.pid"

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

        @app.route("/predict", methods=["POST"])
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
                return jsonify({"error": str(e)}), 500

        print(f"Deploying at http://{host}:{port}/predict")
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
    args = parser.parse_args()

    if args.command == "up":
        print(f"Loading model: {args.model}...")
        try:
            model = pipeline("text-classification", model=args.model)
            print("Model loaded!")
        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            return

        app = Flask(__name__)

        @app.route("/predict", methods=["POST"])
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
                return jsonify({"error": str(e)}), 500

        print(f"Deploying at http://{args.host}:{args.port}/predict")
        app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()
