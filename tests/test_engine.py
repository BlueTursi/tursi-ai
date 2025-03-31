"""
Tests for the tursi engine module.
"""
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from tursi.engine import create_app, ALLOWED_MODELS


@pytest.fixture
def mock_pipeline():
    """Mock the transformers pipeline."""
    with patch('tursi.engine.pipeline') as mock:
        mock.return_value = MagicMock()
        mock.return_value.return_value = [{'label': 'POSITIVE', 'score': 0.9}]
        yield mock


def test_create_app(mock_pipeline):
    """Test that create_app returns a Flask application."""
    app = create_app(ALLOWED_MODELS[0])
    assert isinstance(app, Flask)
    assert app.config['RATE_LIMIT'] == '100 per minute'  # default rate limit


def test_create_app_with_custom_rate_limit(mock_pipeline):
    """Test that create_app accepts custom rate limit."""
    app = create_app(ALLOWED_MODELS[0], rate_limit='50 per minute')
    assert isinstance(app, Flask)
    assert app.config['RATE_LIMIT'] == '50 per minute'


def test_create_app_with_invalid_model():
    """Test that create_app raises error for invalid model."""
    with pytest.raises(ValueError, match=r"Model .* is not in the allowed list"):
        create_app('invalid-model')


def test_predict_endpoint(mock_pipeline):
    """Test the predict endpoint."""
    app = create_app(ALLOWED_MODELS[0])
    client = app.test_client()
    
    # Test without data
    response = client.post('/predict')
    assert response.status_code == 400
    assert b'Request must be JSON' in response.data
    
    # Test with invalid data
    response = client.post('/predict', json={})
    assert response.status_code == 400
    assert b'Invalid input' in response.data
    
    # Test with valid data
    response = client.post('/predict', json={'text': 'Hello, world!'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['label'] == 'POSITIVE'
    assert data['score'] == 0.9


def test_input_validation(mock_pipeline):
    """Test input validation."""
    app = create_app(ALLOWED_MODELS[0])
    client = app.test_client()
    
    # Test with too long input
    long_text = 'x' * 1000
    response = client.post('/predict', json={'text': long_text})
    assert response.status_code == 400
    assert b'Invalid input' in response.data
    
    # Test with non-string input
    response = client.post('/predict', json={'text': 123})
    assert response.status_code == 400
    assert b'Invalid input' in response.data 