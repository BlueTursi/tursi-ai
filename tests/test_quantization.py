import os
import pytest
from tursi.engine import TursiEngine

# Test model name
TEST_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

@pytest.fixture
def engine():
    """Create a TursiEngine instance for testing."""
    return TursiEngine()

def test_quantization_loading(engine):
    """Test that model loads successfully with quantization."""
    try:
        model, tokenizer = engine.load_quantized_model(TEST_MODEL)
        assert model is not None
        assert tokenizer is not None
        assert hasattr(model, 'forward'), "Model should have forward method"
    except Exception as e:
        pytest.fail(f"Failed to load quantized model: {str(e)}")

def test_quantized_inference(engine):
    """Test inference with quantized model."""
    # Load model
    model, tokenizer = engine.load_quantized_model(TEST_MODEL)

    # Test text
    test_text = "This is a great test! I'm very happy."

    # Validate input
    assert engine.validate_input(test_text), "Input validation should pass"

    # Tokenize
    inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)

    # Run inference
    outputs = model(**inputs)
    predictions = outputs.logits.softmax(dim=-1)

    # Check predictions shape and values
    assert len(predictions.shape) == 2, "Predictions should be 2D tensor"
    assert predictions.shape[1] == 2, "Should have 2 classes (positive/negative)"
    assert 0 <= float(predictions[0][0]) <= 1, "Probabilities should be between 0 and 1"
    assert 0 <= float(predictions[0][1]) <= 1, "Probabilities should be between 0 and 1"

    # Sum of probabilities should be close to 1
    assert abs(float(predictions.sum()) - 1.0) < 1e-6, "Probabilities should sum to 1"

def test_quantization_settings(engine):
    """Test that quantization settings are properly set."""
    # Check environment variables
    mode = os.getenv("QUANTIZATION_MODE", "dynamic")
    bits = int(os.getenv("QUANTIZATION_BITS", "8"))

    assert mode in ["dynamic", "static"], "Invalid quantization mode"
    assert bits in [4, 8], "Invalid number of bits for quantization"
