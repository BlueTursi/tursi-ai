"""Tests for the Tursi API server."""

import json
import pytest
from tursi.api import TursiAPI
from tursi.db import TursiDB


@pytest.fixture
def db_path(tmp_path):
    """Provide a temporary database path."""
    return str(tmp_path / "test_tursi.db")


@pytest.fixture
def db(db_path):
    """Provide a database instance."""
    return TursiDB(db_path)


@pytest.fixture
def api(db):
    """Provide an API instance."""
    return TursiAPI(db)


@pytest.fixture
def client(api):
    """Provide a test client."""
    api.app.config["TESTING"] = True
    return api.app.test_client()


@pytest.fixture
def sample_deployment(db):
    """Create a sample deployment and return its ID."""
    config = {"model": "test-model", "quantization": "dynamic", "bits": 8}
    return db.add_deployment(
        model_name="test-model",
        process_id=12345,
        host="localhost",
        port=5000,
        config=config,
    )


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "version" in data


def test_deploy_model(client):
    """Test deploying a new model."""
    payload = {
        "model_name": "test-model",
        "host": "localhost",
        "port": 5000,
        "config": {"quantization": "dynamic", "bits": 8, "rate_limit": "100/minute"},
    }

    response = client.post(
        "/api/v1/models", json=payload, content_type="application/json"
    )

    assert response.status_code == 202
    data = json.loads(response.data)
    assert "deployment_id" in data
    assert data["status"] == "pending"


def test_deploy_model_missing_fields(client):
    """Test deploying a model with missing fields."""
    payload = {
        "model_name": "test-model"
        # Missing required fields
    }

    response = client.post(
        "/api/v1/models", json=payload, content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Missing required fields" in data["error"]


def test_stop_model(client, sample_deployment):
    """Test stopping a model deployment."""
    response = client.delete(f"/api/v1/models/{sample_deployment}")

    assert response.status_code == 202
    data = json.loads(response.data)
    assert data["deployment_id"] == sample_deployment
    assert data["status"] == "stopping"


def test_stop_nonexistent_model(client):
    """Test stopping a model that doesn't exist."""
    response = client.delete("/api/v1/models/999")

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_list_models(client, sample_deployment):
    """Test listing active model deployments."""
    response = client.get("/api/v1/models")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "deployments" in data
    assert len(data["deployments"]) == 1
    assert data["deployments"][0]["id"] == sample_deployment


def test_get_model_status(client, sample_deployment):
    """Test getting status of a specific model."""
    response = client.get(f"/api/v1/models/{sample_deployment}")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == sample_deployment
    assert data["model_name"] == "test-model"


def test_get_nonexistent_model_status(client):
    """Test getting status of a model that doesn't exist."""
    response = client.get("/api/v1/models/999")

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_get_logs(client, sample_deployment, db):
    """Test getting logs for a model deployment."""
    # Add some test logs
    db.add_log(sample_deployment, "INFO", "Test message 1")
    db.add_log(sample_deployment, "ERROR", "Test message 2")

    response = client.get(f"/api/v1/models/{sample_deployment}/logs")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "logs" in data
    assert len(data["logs"]) == 2
    assert data["logs"][0]["message"] == "Test message 2"  # Most recent first
    assert data["logs"][1]["message"] == "Test message 1"


def test_get_logs_with_limit(client, sample_deployment, db):
    """Test getting logs with a limit parameter."""
    # Add test logs
    for i in range(5):
        db.add_log(sample_deployment, "INFO", f"Test message {i}")

    response = client.get(f"/api/v1/models/{sample_deployment}/logs?limit=3")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["logs"]) == 3


def test_get_metrics(client, sample_deployment, db):
    """Test getting metrics for a model deployment."""
    # Add some test metrics
    db.add_metrics(sample_deployment, cpu_percent=50.0, memory_mb=1024.0)
    db.add_metrics(sample_deployment, cpu_percent=60.0, memory_mb=1124.0)

    response = client.get(f"/api/v1/models/{sample_deployment}/metrics")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "metrics" in data
    assert len(data["metrics"]) == 2
    assert data["metrics"][0]["cpu_percent"] == 60.0  # Most recent first
    assert data["metrics"][1]["memory_mb"] == 1024.0


def test_get_metrics_with_limit(client, sample_deployment, db):
    """Test getting metrics with a limit parameter."""
    # Add test metrics
    for i in range(5):
        db.add_metrics(sample_deployment, cpu_percent=50.0 + i, memory_mb=1024.0 + i)

    response = client.get(f"/api/v1/models/{sample_deployment}/metrics?limit=3")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["metrics"]) == 3
