"""
Tests for the tursi engine module.
"""
import pytest
from flask import Flask
from tursi.engine import create_app


def test_create_app():
    """Test that create_app returns a Flask application."""
    app = create_app()
    assert isinstance(app, Flask)
    assert app.config['RATE_LIMIT'] == 100  # default rate limit


def test_create_app_with_custom_rate_limit():
    """Test that create_app accepts custom rate limit."""
    app = create_app(rate_limit=50)
    assert isinstance(app, Flask)
    assert app.config['RATE_LIMIT'] == 50


def test_predict_endpoint():
    """Test the predict endpoint."""
    app = create_app()
    client = app.test_client()
    
    # Test without data
    response = client.post('/predict')
    assert response.status_code == 400
    
    # Test with invalid data
    response = client.post('/predict', json={})
    assert response.status_code == 400
    
    # Test with valid data
    response = client.post('/predict', json={'text': 'Hello, world!'})
    assert response.status_code == 200
    assert 'prediction' in response.json 