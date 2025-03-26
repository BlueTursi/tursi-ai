import argparse
from transformers import pipeline
from flask import Flask, request, jsonify

# CLI setup
parser = argparse.ArgumentParser(description="tursi-engine: Deploy AI models locally")
parser.add_argument("up", nargs="?", help="Deploy a model (use 'up')")
parser.add_argument("--model", default="distilbert-base-uncased-finetuned-sst-2-english", 
                    help="Hugging Face model name (default: distilbert-sst2)")
parser.add_argument("--port", type=int, default=5000, help="Port to run server on (default: 5000)")
args = parser.parse_args()

# App logic
if args.up == "up":
    # Load model
    print(f"Loading model: {args.model}...")
    try:
        model = pipeline("text-classification", model=args.model)
    except Exception as e:
        print(f"Error loading model: {e}")
        exit(1)
    print("Model loaded!")

    # Flask setup
    app = Flask(__name__)

    @app.route("/predict", methods=["POST"])
    def predict():
        text = request.json.get("text", "")
        result = model(text)
        return jsonify(result[0])

    # Run server
    print(f"Deploying at http://localhost:{args.port}/predict")
    app.run(host="0.0.0.0", port=args.port)
else:
    print("Usage: tursi-engine up --model <model-name> [--port <port>]")