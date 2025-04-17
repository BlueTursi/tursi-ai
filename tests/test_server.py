import os
import json
import pytest
import requests
import time
from multiprocessing import Process
from tursi.engine import create_app

def run_server():
    """Helper function to run the server in a separate process."""
    app = create_app("distilbert-base-uncased-finetuned-sst-2-english")
    app.run(host="127.0.0.1", port=5000)

def wait_for_server(url, timeout=30, interval=1):
    """Wait for server to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(url)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(interval)
    return False

@pytest.fixture(scope="module")
def server():
    """Fixture to start and stop the server for testing."""
    # Set quantization settings
    os.environ["QUANTIZATION_MODE"] = "dynamic"
    os.environ["QUANTIZATION_BITS"] = "8"

    # Start server in a separate process
    server_process = Process(target=run_server)
    server_process.start()

    # Wait for server to start
    server_url = "http://127.0.0.1:5000"
    if not wait_for_server(server_url):
        pytest.fail(f"Server failed to start within timeout")

    yield

    # Cleanup
    server_process.terminate()
    server_process.join()

def test_server_prediction(server):
    """Test that server responds correctly with quantized model."""
    url = "http://127.0.0.1:5000/predict"

    try:
        # Test positive text
        positive_data = {"text": "This is amazing! I love it!"}
        response = requests.post(url, json=positive_data)
        assert response.status_code == 200
        result = response.json()
        assert "label" in result
        assert "score" in result
        assert result["label"] in ["POSITIVE", "NEGATIVE"]
        assert 0 <= result["score"] <= 1

        # Test negative text
        negative_data = {"text": "This is terrible! I hate it!"}
        response = requests.post(url, json=negative_data)
        assert response.status_code == 200
        result = response.json()
        assert result["label"] in ["POSITIVE", "NEGATIVE"]
        assert 0 <= result["score"] <= 1
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to connect to server: {str(e)}")
