"""Integration tests for Tursi components."""

import os
import time
import signal
import pytest
import requests
import threading
import logging
from unittest.mock import patch, Mock
from tursi.daemon import TursiDaemon
from tursi.model import ModelManager
from tursi.db import TursiDB

# Use different port ranges for each test to avoid conflicts
PORT_RANGES = {
    "deployment": (6000, 6010),
    "logs": (6020, 6030),
    "multiple": (6040, 6050),
    "recovery": (6060, 6070),
    "reload": (6080, 6090),
}


@pytest.fixture
def db_path(tmp_path):
    """Provide a temporary database path."""
    return str(tmp_path / "test_tursi.db")


@pytest.fixture
def pid_file(tmp_path):
    """Provide a temporary PID file path."""
    return str(tmp_path / "tursid.pid")


@pytest.fixture
def api_port():
    """Get a unique API port for each test."""
    return 6100


@pytest.fixture
def daemon(db_path, pid_file, api_port):
    """Create a daemon instance with test configuration."""
    # Ensure clean database for each test
    if os.path.exists(db_path):
        os.remove(db_path)

    daemon = TursiDaemon(
        pid_file=pid_file, db_path=db_path, api_host="localhost", api_port=api_port
    )

    # Configure logging to prevent closed file errors
    daemon.logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    daemon.logger.addHandler(handler)

    yield daemon

    # Cleanup
    daemon.cleanup()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def mock_model():
    """Create a mock model."""
    model = Mock()
    model.generate.return_value = [[1, 2, 3]]  # Mock token IDs
    return model


@pytest.fixture
def mock_tokenizer():
    """Create a mock tokenizer."""
    tokenizer = Mock()
    tokenizer.encode.return_value = [1, 2, 3]
    tokenizer.decode.return_value = "Generated text"
    return tokenizer


def wait_for_server(port, timeout=5):
    """Wait for server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(f"http://localhost:{port}/api/v1/health")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False


@pytest.mark.integration
def test_daemon_model_deployment(daemon, api_port):
    """Test model deployment through the daemon API."""
    api_thread = threading.Thread(target=daemon.run)
    api_thread.daemon = True
    api_thread.start()

    assert wait_for_server(api_port), "API server failed to start"

    try:
        # Deploy a model via API
        response = requests.post(
            f"http://localhost:{api_port}/api/v1/models",
            json={
                "model_name": "test-model",
                "host": "localhost",
                "port": PORT_RANGES["deployment"][0],
                "config": {
                    "quantization": "dynamic",
                    "bits": 8,
                    "rate_limit": "100/minute",
                },
            },
        )
        assert response.status_code == 202
        deployment_id = response.json()["deployment_id"]

        # Wait for deployment to start
        time.sleep(2)

        # Check deployment status
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}"
        )
        assert response.status_code == 200
        assert response.json()["status"] in ["running", "pending"]

        # Stop the deployment
        response = requests.delete(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}"
        )
        assert response.status_code == 202

        # Verify deployment is stopped
        time.sleep(1)
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "stopping"

    finally:
        daemon.is_running = False
        api_thread.join(timeout=5)


@pytest.mark.integration
def test_daemon_model_logs_and_metrics(daemon, api_port):
    """Test model logs and metrics collection."""
    api_thread = threading.Thread(target=daemon.run)
    api_thread.daemon = True
    api_thread.start()

    assert wait_for_server(api_port), "API server failed to start"

    try:
        # Deploy a model
        response = requests.post(
            f"http://localhost:{api_port}/api/v1/models",
            json={
                "model_name": "test-model",
                "host": "localhost",
                "port": PORT_RANGES["logs"][0],
                "config": {"quantization": "dynamic", "bits": 8},
            },
        )
        assert response.status_code == 202
        deployment_id = response.json()["deployment_id"]

        # Wait for deployment and metrics collection
        time.sleep(2)

        # Add a test log directly
        daemon.db.add_log(deployment_id, "INFO", "Test log message")

        # Check logs
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}/logs"
        )
        assert response.status_code == 200
        logs = response.json()["logs"]
        assert len(logs) > 0
        assert any("Test log message" in log["message"] for log in logs)

        # Add test metrics directly
        daemon.db.add_metrics(deployment_id, cpu_percent=50.0, memory_mb=1024.0)

        # Check metrics
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}/metrics"
        )
        assert response.status_code == 200
        metrics = response.json()["metrics"]
        assert len(metrics) > 0
        assert metrics[0]["cpu_percent"] == 50.0
        assert metrics[0]["memory_mb"] == 1024.0

    finally:
        daemon.is_running = False
        api_thread.join(timeout=5)


@pytest.mark.integration
def test_daemon_multiple_models(daemon, api_port):
    """Test running multiple model deployments simultaneously."""
    api_thread = threading.Thread(target=daemon.run)
    api_thread.daemon = True
    api_thread.start()

    assert wait_for_server(api_port), "API server failed to start"

    deployment_ids = []
    try:
        # Deploy multiple models
        for i, port in enumerate(
            range(PORT_RANGES["multiple"][0], PORT_RANGES["multiple"][0] + 2)
        ):
            response = requests.post(
                f"http://localhost:{api_port}/api/v1/models",
                json={
                    "model_name": f"test-model-{port}",
                    "host": "localhost",
                    "port": port,
                    "config": {"quantization": "dynamic", "bits": 8},
                },
            )
            assert response.status_code == 202
            deployment_ids.append(response.json()["deployment_id"])

        # Wait for deployments to start
        time.sleep(2)

        # List all models
        response = requests.get(f"http://localhost:{api_port}/api/v1/models")
        assert response.status_code == 200
        deployments = response.json()["deployments"]
        assert len(deployments) == 2

        # Verify each deployment
        for deployment_id in deployment_ids:
            response = requests.get(
                f"http://localhost:{api_port}/api/v1/models/{deployment_id}"
            )
            assert response.status_code == 200
            assert response.json()["status"] in ["running", "pending"]

    finally:
        daemon.is_running = False
        api_thread.join(timeout=5)


@pytest.mark.integration
def test_daemon_process_recovery(daemon, api_port):
    """Test daemon's ability to recover from process failures."""
    api_thread = threading.Thread(target=daemon.run)
    api_thread.daemon = True
    api_thread.start()

    assert wait_for_server(api_port), "API server failed to start"

    try:
        # Deploy a model
        response = requests.post(
            f"http://localhost:{api_port}/api/v1/models",
            json={
                "model_name": "test-model",
                "host": "localhost",
                "port": PORT_RANGES["recovery"][0],
                "config": {"quantization": "dynamic", "bits": 8},
            },
        )
        assert response.status_code == 202
        deployment_id = response.json()["deployment_id"]

        # Wait for deployment to start and process to be registered
        time.sleep(2)

        # Add a mock process to simulate failure
        mock_process = Mock()
        mock_process.process = Mock()
        daemon.model_processes[deployment_id] = mock_process

        # Simulate process failure
        mock_process.process.terminate()

        # Wait for daemon to detect and handle failure
        time.sleep(2)

        # Check deployment status
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "failed"

        # Verify error is logged
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}/logs"
        )
        assert response.status_code == 200
        logs = response.json()["logs"]
        assert len(logs) > 0

    finally:
        daemon.is_running = False
        api_thread.join(timeout=5)


@pytest.mark.integration
def test_daemon_reload_config(daemon, api_port):
    """Test daemon configuration reload on SIGHUP."""
    api_thread = threading.Thread(target=daemon.run)
    api_thread.daemon = True
    api_thread.start()

    assert wait_for_server(api_port), "API server failed to start"

    try:
        # Deploy a model
        response = requests.post(
            f"http://localhost:{api_port}/api/v1/models",
            json={
                "model_name": "test-model",
                "host": "localhost",
                "port": PORT_RANGES["reload"][0],
                "config": {"quantization": "dynamic", "bits": 8},
            },
        )
        assert response.status_code == 202
        deployment_id = response.json()["deployment_id"]

        # Wait for deployment to start
        time.sleep(2)

        # Simulate SIGHUP
        os.kill(os.getpid(), signal.SIGHUP)

        # Wait for reload
        time.sleep(2)

        # Verify deployment is still running
        response = requests.get(
            f"http://localhost:{api_port}/api/v1/models/{deployment_id}"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "running"

    finally:
        daemon.is_running = False
        api_thread.join(timeout=5)
