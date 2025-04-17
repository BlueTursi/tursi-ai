"""Tests for the Tursi Daemon (tursid)."""

import os
import signal
import time
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from tursi.daemon import TursiDaemon, ModelProcess


@pytest.fixture
def temp_pid_file(tmp_path):
    """Provide a temporary PID file path."""
    return str(tmp_path / "test_tursid.pid")


@pytest.fixture
def temp_db_path(tmp_path):
    """Provide a temporary database path."""
    return str(tmp_path / "test_tursi.db")


@pytest.fixture
def daemon(temp_pid_file, temp_db_path):
    """Create a daemon instance with temporary paths."""
    return TursiDaemon(pid_file=temp_pid_file, db_path=temp_db_path)


@pytest.fixture
def sample_deployment():
    """Create a sample deployment configuration."""
    return {
        "id": 1,
        "model_name": "test-model",
        "process_id": None,
        "host": "localhost",
        "port": 5000,
        "status": "pending",
        "config": json.dumps(
            {"quantization": "dynamic", "bits": 8, "rate_limit": "100/minute"}
        ),
    }


def test_daemon_initialization(daemon, temp_pid_file, temp_db_path):
    """Test daemon initialization."""
    assert daemon.pid_file == temp_pid_file
    assert daemon.db.db_path == temp_db_path
    assert not daemon.is_running
    assert len(daemon.model_processes) == 0


@patch("tursi.daemon.ModelProcess")
def test_start_deployment(mock_model_process, daemon, sample_deployment):
    """Test starting a model deployment."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.start.return_value = 12345
    mock_model_process.return_value = mock_instance

    # Start deployment
    daemon._start_deployment(sample_deployment)

    # Verify process creation
    mock_model_process.assert_called_once_with(
        model_name="test-model",
        host="localhost",
        port=5000,
        config={"quantization": "dynamic", "bits": 8, "rate_limit": "100/minute"},
    )
    mock_instance.start.assert_called_once()

    # Verify process tracking
    assert len(daemon.model_processes) == 1
    assert 1 in daemon.model_processes

    # Verify database updates
    deployment = daemon.db.get_deployment(1)
    assert deployment["status"] == "running"

    # Verify logs
    logs = daemon.db.get_logs(1)
    assert len(logs) == 1
    assert "Started model process with PID 12345" in logs[0]["message"]


@patch("tursi.daemon.ModelProcess")
def test_stop_deployment(mock_model_process, daemon, sample_deployment):
    """Test stopping a model deployment."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.start.return_value = 12345
    mock_model_process.return_value = mock_instance

    # Start and then stop deployment
    daemon._start_deployment(sample_deployment)
    daemon._stop_deployment(1)

    # Verify process cleanup
    mock_instance.stop.assert_called_once()
    assert len(daemon.model_processes) == 0

    # Verify database updates
    deployment = daemon.db.get_deployment(1)
    assert deployment["status"] == "stopped"

    # Verify logs
    logs = daemon.db.get_logs(1)
    assert len(logs) == 2
    assert "Stopped model process" in logs[0]["message"]


@patch("tursi.daemon.psutil.Process")
@patch("tursi.daemon.ModelProcess")
def test_update_metrics(
    mock_model_process, mock_psutil_process, daemon, sample_deployment
):
    """Test updating resource metrics."""
    # Setup mocks
    mock_instance = MagicMock()
    mock_instance.start.return_value = 12345
    mock_instance.process.pid = 12345
    mock_instance.process.is_alive.return_value = True
    mock_model_process.return_value = mock_instance

    mock_process = MagicMock()
    mock_process.cpu_percent.return_value = 50.0
    mock_process.memory_info.return_value = MagicMock(rss=1024 * 1024 * 100)  # 100MB
    mock_psutil_process.return_value = mock_process

    # Start deployment and update metrics
    daemon._start_deployment(sample_deployment)
    daemon._update_metrics()

    # Verify metrics collection
    metrics = daemon.db.get_metrics(1)
    assert len(metrics) == 1
    assert metrics[0]["cpu_percent"] == 50.0
    assert metrics[0]["memory_mb"] == 100.0


def test_cleanup_old_metrics(daemon, sample_deployment):
    """Test cleaning up old metrics."""
    # Add deployment and metrics
    deployment_id = daemon.db.add_deployment(
        model_name=sample_deployment["model_name"],
        process_id=12345,
        host=sample_deployment["host"],
        port=sample_deployment["port"],
        config=json.loads(sample_deployment["config"]),
    )

    # Add metrics
    daemon.db.add_metrics(deployment_id, 50.0, 100.0)

    # Clean up metrics
    daemon.db.cleanup_old_metrics(max_age_hours=0)  # Clean all metrics

    # Verify cleanup
    metrics = daemon.db.get_metrics(deployment_id)
    assert len(metrics) == 0


@patch("tursi.daemon.ModelProcess")
def test_reload_config(mock_model_process, daemon, sample_deployment):
    """Test reloading configuration."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.start.return_value = 12345
    mock_model_process.return_value = mock_instance

    # Add deployment to database
    deployment_id = daemon.db.add_deployment(
        model_name=sample_deployment["model_name"],
        process_id=12345,
        host=sample_deployment["host"],
        port=sample_deployment["port"],
        config=json.loads(sample_deployment["config"]),
    )

    # Reload config
    daemon._reload_config()

    # Verify process started
    assert len(daemon.model_processes) == 1
    mock_model_process.assert_called_once()
    mock_instance.start.assert_called_once()


def test_signal_handling(daemon):
    """Test signal handling."""
    with patch.object(daemon, "stop") as mock_stop:
        # Test SIGTERM
        daemon._handle_signal(signal.SIGTERM, None)
        mock_stop.assert_called_once()

    with patch.object(daemon, "_reload_config") as mock_reload:
        # Test SIGHUP
        daemon._handle_signal(signal.SIGHUP, None)
        mock_reload.assert_called_once()


def test_model_process():
    """Test ModelProcess class."""
    config = {"rate_limit": "100/minute"}
    process = ModelProcess("test-model", "localhost", 5000, config)

    # Test initialization
    assert process.model_name == "test-model"
    assert process.host == "localhost"
    assert process.port == 5000
    assert process.config == config
    assert process.process is None

    # Test stop without start
    process.stop()  # Should not raise any errors


@patch("tursi.daemon.TursiEngine")
def test_model_process_run(mock_engine, tmp_path):
    """Test ModelProcess run method."""
    # Setup mocks
    mock_app = MagicMock()
    mock_engine_instance = MagicMock()
    mock_engine_instance.create_app.return_value = mock_app
    mock_engine.return_value = mock_engine_instance

    # Create and start process
    process = ModelProcess("test-model", "localhost", 5000, {})
    with patch("multiprocessing.Process.start") as mock_start:
        pid = process.start()
        mock_start.assert_called_once()
        assert pid is not None
