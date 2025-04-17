"""Tests for model management and deployment."""
import pytest
import threading
import requests
from unittest.mock import Mock, patch
from tursi.model import ModelManager, ModelServer

@pytest.fixture
def model_manager():
    """Create a model manager instance."""
    return ModelManager()

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

@pytest.fixture
def mock_server(mock_model, mock_tokenizer):
    """Create a mock model server."""
    server = ModelServer("test-model", mock_model, mock_tokenizer)
    return server

def test_model_server_init(mock_server):
    """Test ModelServer initialization."""
    assert mock_server.model_name == "test-model"
    assert mock_server.app is not None
    assert mock_server.rate_limit is None

def test_model_server_generate(mock_server):
    """Test model generation endpoint."""
    with mock_server.app.test_client() as client:
        # Test valid request
        response = client.post('/v1/generate', json={
            'prompt': 'Test prompt',
            'max_length': 50,
            'temperature': 0.8
        })
        assert response.status_code == 200
        assert 'generated_text' in response.json

        # Test missing prompt
        response = client.post('/v1/generate', json={})
        assert response.status_code == 400
        assert 'error' in response.json

def test_model_server_health_check(mock_server):
    """Test health check endpoint."""
    with mock_server.app.test_client() as client:
        response = client.get('/v1/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
        assert response.json['model'] == 'test-model'

@patch('tursi.model.AutoModelForCausalLM')
@patch('tursi.model.AutoTokenizer')
def test_model_manager_load_model(mock_auto_tokenizer, mock_auto_model, model_manager):
    """Test model loading."""
    # Setup mocks
    mock_tokenizer = Mock()
    mock_model = Mock()
    mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer
    mock_auto_model.from_pretrained.return_value = mock_model

    # Test loading without quantization
    model, tokenizer = model_manager.load_model("test/model")
    assert model == mock_model
    assert tokenizer == mock_tokenizer

    # Test loading with quantization
    model, tokenizer = model_manager.load_model(
        "test/model",
        quantization="dynamic",
        bits=8
    )
    assert model == mock_model
    assert tokenizer == mock_tokenizer

def test_model_manager_deploy_model(model_manager, mock_model, mock_tokenizer):
    """Test model deployment."""
    with patch('tursi.model.ModelServer') as mock_server_class, \
         patch('tursi.model.make_server') as mock_make_server:

        # Setup mocks
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        mock_server_instance = Mock()
        mock_make_server.return_value = mock_server_instance

        # Mock model loading
        model_manager.load_model = Mock(return_value=(mock_model, mock_tokenizer))

        # Test deployment
        model_manager.deploy_model(
            model_name="test/model",
            host="localhost",
            port=5000
        )

        assert 5000 in model_manager.servers
        assert model_manager.servers[5000]["server"] == mock_server_instance
        assert isinstance(model_manager.servers[5000]["thread"], threading.Thread)

        # Test duplicate port
        with pytest.raises(ValueError):
            model_manager.deploy_model(
                model_name="test/model",
                host="localhost",
                port=5000
            )

def test_model_manager_stop_model(model_manager):
    """Test stopping a model deployment."""
    # Setup mock server
    mock_server = Mock()
    mock_thread = Mock()
    mock_stop_event = threading.Event()

    model_manager.servers[5000] = {
        "server": mock_server,
        "thread": mock_thread,
        "stop_event": mock_stop_event,
        "model_name": "test/model"
    }

    # Test stopping
    model_manager.stop_model(5000)

    assert mock_server.shutdown.called
    assert mock_thread.join.called
    assert 5000 not in model_manager.servers

    # Test stopping non-existent deployment
    with pytest.raises(ValueError):
        model_manager.stop_model(6000)

def test_model_manager_cleanup(model_manager):
    """Test cleanup of all deployments."""
    # Setup mock servers
    ports = [5000, 5001]
    for port in ports:
        mock_server = Mock()
        mock_thread = Mock()
        mock_stop_event = threading.Event()

        model_manager.servers[port] = {
            "server": mock_server,
            "thread": mock_thread,
            "stop_event": mock_stop_event,
            "model_name": f"test/model-{port}"
        }

    # Test cleanup
    model_manager.cleanup()

    assert len(model_manager.servers) == 0
    assert len(model_manager.models) == 0
