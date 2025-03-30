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
    # Check if running in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Error: tursi requires a virtual environment for safe installation.")
        print("Run: python -m venv venv && source venv/bin/activate && pip install .")
        print("Or install directly from PyPI: pip install tursi")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="tursi-engine: Deploy an AI model with Flask")
    parser.add_argument("command", choices=["up", "down"], help="Command to run ('up' to start, 'down' to stop)")
    parser.add_argument("--model", default="distilbert-base-uncased-finetuned-sst-2-english",
                        help="Model name from Hugging Face (default: distilbert-base-uncased-finetuned-sst-2-english)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the server on (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on (default: 5000)")
    args = parser.parse_args()

    if args.command == "up":
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            if is_server_running(pid):
                print("Server already running. Use 'tursi-engine down' to stop it first.")
                sys.exit(1)
            else:
                print("Found stale PID file. Cleaning up.")
                os.remove(PID_FILE)

        # Start server in a new process
        p = Process(target=run_server, args=(args.model, args.host, args.port))
        p.start()
        
        # Save PID immediately
        with open(PID_FILE, "w") as f:
            f.write(str(p.pid))
        time.sleep(1)  # Short wait to ensure it starts
        if not p.is_alive():
            print("Server failed to start. Check logs for details.")
            os.remove(PID_FILE)
            sys.exit(1)
        
        print(f"Server started with PID {p.pid}. Use 'tursi-engine down' to stop.")
        sys.exit(0)

    elif args.command == "down":
        if not os.path.exists(PID_FILE):
            print("No server running (PID file not found).")
            sys.exit(1)
        
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        
        if is_server_running(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                for _ in range(5):
                    if not is_server_running(pid):
                        break
                    time.sleep(1)
                else:
                    os.kill(pid, signal.SIGKILL)
                print(f"Server (PID {pid}) stopped successfully.")
            except Exception as e:
                print(f"Failed to stop server: {str(e)}")
                sys.exit(1)
        else:
            print("Server process not found. Cleaning up PID file.")
        
        os.remove(PID_FILE)

if __name__ == "__main__":
    main()
