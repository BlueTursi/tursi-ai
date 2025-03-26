from transformers import pipeline
from flask import Flask, request, jsonify

print("Loading model...")
model = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
print("Model loaded!")

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    text = request.json.get("text", "")
    result = model(text)
    return jsonify(result[0])

print("Deploying at http://localhost:5000/predict")
app.run(host="0.0.0.0", port=5000)