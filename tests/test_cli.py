"""Tests for the CLI interface."""

import os
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from typer.testing import CliRunner
from tursi.cli import app
from tursi import __version__

# Create test runner
runner = CliRunner()


def test_version():
    """Test version flag shows correct version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


@pytest.mark.parametrize("help_flag", ["-h", "--help"])
def test_help(help_flag):
    """Test help flags show help text."""
    result = runner.invoke(app, [help_flag])
    assert result.exit_code == 0
    assert (
        "Tursi Engine - An open-source framework to compose and deploy AI models with ease"
        in result.stdout
    )
    assert "Commands:" in result.stdout
    assert "up" in result.stdout
    assert "down" in result.stdout


@patch("tursi.cli.TursiEngine")
def test_up_basic(mock_engine):
    """Test basic model deployment with default options."""
    # Setup mock
    mock_engine_instance = Mock()
    mock_engine.return_value = mock_engine_instance
    mock_app = Mock()
    mock_engine_instance.create_app.return_value = mock_app

    # Run command
    result = runner.invoke(app, ["up", "distilbert-base-uncased"])

    # Check exit code
    assert result.exit_code == 0

    # Verify engine initialization
    mock_engine.assert_called_once()

    # Verify model deployment
    mock_engine_instance.create_app.assert_called_once_with(
        model_name="distilbert-base-uncased", rate_limit="100/minute"
    )

    # Check output messages
    assert "Deploying model with Tursi Engine" in result.stdout
    assert "Model is running at http://127.0.0.1:5000" in result.stdout


@patch("tursi.cli.TursiEngine")
def test_up_with_options(mock_engine):
    """Test model deployment with custom options."""
    # Setup mock
    mock_engine_instance = Mock()
    mock_engine.return_value = mock_engine_instance
    mock_app = Mock()
    mock_engine_instance.create_app.return_value = mock_app

    # Run command with options
    result = runner.invoke(
        app,
        [
            "up",
            "bert-base-uncased",
            "--port",
            "8000",
            "--host",
            "0.0.0.0",
            "--quantization",
            "static",
            "--bits",
            "4",
            "--rate-limit",
            "200/minute",
            "--cache-dir",
            "/tmp/models",
        ],
    )

    # Check exit code
    assert result.exit_code == 0

    # Verify engine configuration
    mock_engine_instance.setup_model_cache.assert_called_once()
    assert mock_engine_instance.MODEL_CACHE_DIR == Path("/tmp/models")
    assert mock_engine_instance.QUANTIZATION_MODE == "static"
    assert mock_engine_instance.QUANTIZATION_BITS == 4

    # Verify model deployment
    mock_engine_instance.create_app.assert_called_once_with(
        model_name="bert-base-uncased", rate_limit="200/minute"
    )

    # Check output messages
    assert "Model is running at http://0.0.0.0:8000" in result.stdout


@patch("tursi.cli.TursiEngine")
def test_up_error_handling(mock_engine):
    """Test error handling during model deployment."""
    # Setup mock to raise an error
    mock_engine.side_effect = ValueError("Invalid model name")

    # Run command
    result = runner.invoke(app, ["up", "invalid-model"])

    # Check error handling
    assert result.exit_code == 1
    assert "Error:" in result.stdout
    assert "Invalid model name" in result.stdout


def test_up_missing_model():
    """Test deployment without required model argument."""
    result = runner.invoke(app, ["up"])
    assert result.exit_code != 0
    assert "Missing argument" in result.stdout


@pytest.mark.parametrize("invalid_bits", [-1, 0, 3, 5, 16])
def test_up_invalid_quantization_bits(invalid_bits):
    """Test deployment with invalid quantization bits."""
    result = runner.invoke(
        app, ["up", "bert-base-uncased", "--bits", str(invalid_bits)]
    )
    assert result.exit_code != 0
    assert "Invalid value" in result.stdout


@pytest.mark.parametrize("invalid_mode", ["fast", "slow", "medium"])
def test_up_invalid_quantization_mode(invalid_mode):
    """Test deployment with invalid quantization mode."""
    result = runner.invoke(
        app, ["up", "bert-base-uncased", "--quantization", invalid_mode]
    )
    assert result.exit_code != 0
    assert "Invalid value" in result.stdout


@patch("tursi.cli.TursiEngine")
def test_down(mock_engine):
    """Test stopping the model deployment."""
    mock_engine_instance = Mock()
    mock_engine.return_value = mock_engine_instance

    result = runner.invoke(app, ["down"])
    assert result.exit_code == 0
    assert "Stopping model deployment" in result.stdout
    mock_engine_instance.stop_all.assert_called_once()


# Future tests to be implemented as features are added:
# def test_ps():
#     """Test listing running models."""
#     pass

# def test_logs():
#     """Test viewing model logs."""
#     pass

# def test_stats():
#     """Test viewing resource usage statistics."""
#     pass
