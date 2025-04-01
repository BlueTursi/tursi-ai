# tursi-ai

[![GitHub release](https://img.shields.io/github/v/release/BlueTursi/tursi-ai)](https://github.com/BlueTursi/tursi-ai/releases)
[![Tests](https://github.com/BlueTursi/tursi-ai/actions/workflows/test.yml/badge.svg)](https://github.com/BlueTursi/tursi-ai/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen.svg)](https://github.com/BlueTursi/tursi-ai)

A simple framework to deploy AI models locally with one command, no containers needed. Features efficient model quantization for reduced memory usage and faster inference.

## Features

- Deploy AI models locally with one command
- No containers needed
- Simple API interface
- Rate limiting and security features
- Automated versioning and releases
- CI/CD pipeline with automated testing
- Automated GitHub releases
- Comprehensive test coverage
- Poetry dependency management
- Input validation and error handling
- Configurable rate limiting
- Secure model loading
- Edge-efficient model quantization
  - Dynamic and static quantization support
  - 4-bit and 8-bit quantization options
  - Optimized for CPU inference

## Installation

```bash
pip install tursi
```

## Usage

### Basic Usage

```bash
# Start the server with default settings (dynamic 8-bit quantization)
tursi-engine up

# Start with custom quantization settings
tursi-engine up --quantization-mode dynamic --quantization-bits 8
```

### Making Predictions

```bash
# Test with positive sentiment
curl -X POST -H "Content-Type: application/json" \
     -d '{"text": "This is a great product! I love it!"}' \
     http://localhost:5000/predict

# Example response:
# {"label": "POSITIVE", "score": 0.9998828172683716}

# Test with negative sentiment
curl -X POST -H "Content-Type: application/json" \
     -d '{"text": "This product is terrible, I regret buying it."}' \
     http://localhost:5000/predict

# Example response:
# {"label": "NEGATIVE", "score": 0.9995611310005188}
```

## API Reference

### POST /predict

Endpoint for making predictions using the loaded model.

**Request Body:**
```json
{
    "text": "Your text here"
}
```

**Response:**
```json
{
    "label": "POSITIVE",
    "score": 0.9
}
```

## Configuration

The following environment variables can be set:

- `RATE_LIMIT`: API rate limit (default: "100 per minute")
- `RATE_LIMIT_STORAGE_URI`: Storage backend for rate limiting (default: "memory://")
- `QUANTIZATION_MODE`: Quantization mode (default: "dynamic")
- `QUANTIZATION_BITS`: Number of bits for quantization (default: 8)

### Quantization Options

- **Mode**:
  - `dynamic`: Quantization is performed at runtime (default)
    - Best for general use cases
    - Maintains good accuracy while reducing model size
  - `static`: Quantization is performed during model loading
    - Better performance for specific use cases
    - Requires calibration data

- **Bits**:
  - `8`: 8-bit quantization (default)
    - Good balance between compression and accuracy
    - Recommended for most use cases
  - `4`: 4-bit quantization
    - More aggressive compression
    - May impact accuracy
    - Best for resource-constrained environments

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/BlueTursi/tursi-ai.git
cd tursi-ai

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run tests
poetry run pytest tests/ -v --cov=tursi

# Build package
poetry build
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

[MIT License](/LICENSE)

## Acknowledgments

Built with 💙 using:
- Transformers
- Flask
- PyTorch
- Poetry
- ONNX Runtime
- Optimum

Built by [BlueTursi](https://bluetursi.com).
