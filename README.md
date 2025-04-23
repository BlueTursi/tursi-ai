# tursi-ai

[![GitHub release](https://img.shields.io/github/v/release/BlueTursi/tursi-ai)](https://github.com/BlueTursi/tursi-ai/releases)
[![CI](https://github.com/BlueTursi/tursi-ai/workflows/CI/badge.svg)](https://github.com/BlueTursi/tursi-ai/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen.svg)](https://github.com/BlueTursi/tursi-ai)

Deploy AI models with unmatched simplicity - zero container overhead. Features efficient model quantization for reduced memory usage and faster inference, perfect for resource-constrained environments like IoT and Edge devices.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Common Use Cases](#common-use-cases)
- [Command Reference](#command-reference)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Development](#development)
- [Troubleshooting](docs/troubleshooting.md)

## Features

- Intuitive command-line interface for model deployment
- Zero container overhead - lightweight and efficient
- Optimized for resource-constrained environments
- Simple API interface
- Built-in security features
- Edge-efficient model quantization
  - Dynamic and static quantization support
  - 4-bit and 8-bit quantization options
  - Optimized for CPU inference
- Rate limiting and monitoring
- Automated versioning and releases

## Installation

```bash
pip install tursi
```

## Quick Start

```bash
# Start a model server
tursi up distilbert-base-uncased

# Start with custom settings
tursi up distilbert-base-uncased --port 8000 --quantization dynamic --bits 4

# List running models
tursi ps

# View server logs
tursi logs

# Check resource usage
tursi stats

# Stop the server
tursi down
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

## Command Reference

### tursi up

Start a model server.

```bash
tursi up [OPTIONS] MODEL_NAME

Options:
  --port, -p INTEGER          Port to run the API server on (default: 5000)
  --host TEXT                 Host to bind the API server to (default: 127.0.0.1)
  --quantization, -q TEXT     Quantization mode: 'dynamic' or 'static' (default: dynamic)
  --bits, -b INTEGER         Number of bits for quantization (4 or 8) (default: 8)
  --rate-limit, -r TEXT      API rate limit (default: "100/minute")
  --cache-dir, -c PATH       Directory to cache models (default: ~/.tursi/models)
  -h, --help                 Show this message and exit
```

### tursi down

Stop a running model server.

```bash
tursi down
```

### tursi ps

List running models.

```bash
tursi ps
```

### tursi logs

View server logs.

```bash
tursi logs [OPTIONS]

Options:
  --follow, -f    Follow log output
  --tail INTEGER  Number of lines to show (default: all)
```

### tursi stats

Show resource usage statistics.

```bash
tursi stats
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

# Run tests with coverage
poetry run pytest tests/ -v --cov=tursi --cov-report=xml

# Build package
poetry build
```

### Release Process

For detailed information about the release process, please refer to [RELEASE.md](RELEASE.md).

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

## Common Use Cases

### 1. Edge Device Deployment
```bash
# Deploy a lightweight model optimized for edge devices
tursi up microsoft/squeezebert-mnli --bits 4 --quantization dynamic \
  --rate-limit "50/minute" --port 8080

# Monitor resource usage to ensure it fits device constraints
tursi stats
```

### 2. Production API Server
```bash
# Deploy a robust model with appropriate rate limiting
tursi up bert-base-uncased \
  --host 0.0.0.0 \
  --port 443 \
  --rate-limit "1000/minute" \
  --cache-dir /opt/tursi/models

# Monitor the deployment
tursi logs --follow
```

### 3. Local Development
```bash
# Quick deployment for testing
tursi up distilbert-base-uncased

# In another terminal, test the API
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing the model"}' \
  http://localhost:5000/predict
```

### 4. Multi-Model Setup
```bash
# Deploy sentiment analysis model
tursi up distilbert-base-uncased --port 5000

# Deploy named entity recognition model
tursi up dslim/bert-base-NER --port 5001

# List all running models
tursi ps
```

### 5. Resource-Constrained Environments
```bash
# Deploy with maximum compression
tursi up distilbert-base-uncased \
  --bits 4 \
  --quantization static \
  --rate-limit "20/minute"

# Monitor memory usage
tursi stats
```

Each use case demonstrates different aspects of Tursi's capabilities:
- Edge deployment with 4-bit quantization for minimal resource usage
- Production setup with appropriate host/port configuration
- Local development workflow
- Running multiple models simultaneously
- Maximum compression for resource-constrained environments

## Best Practices

### Resource Management
- Start with 8-bit quantization and monitor performance
- Switch to 4-bit if memory constraints are tight
- Use `tursi stats` to monitor resource usage
- Set appropriate rate limits based on hardware capacity

### Production Deployment
- Always set explicit `--host` and `--port` values
- Configure appropriate rate limits
- Use a dedicated cache directory
- Monitor logs with `tursi logs --follow`
- Set up health monitoring using the `/health` endpoint

### Development Workflow
- Use default settings for quick iterations
- Test different quantization options
- Monitor memory usage with `tursi stats`
- Use `curl` or Postman for API testing
