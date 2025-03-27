import argparse
import requests
import json

def main():
    parser = argparse.ArgumentParser(description="tursi-test: Test a deployed tursi-engine model")
    parser.add_argument("--prompt", required=True, help="Text to send to the model (e.g., 'I love AI')")
    parser.add_argument("--url", default="http://localhost:5000/predict",
                        help="URL of the tursi-engine server (default: http://localhost:5000/predict)")
    args = parser.parse_args()

    payload = {"text": args.prompt}
    try:
        response = requests.post(args.url, json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to get a response from {args.url}")
        print(f"Details: {e}")
        exit(1)

if __name__ == "__main__":
    main()
