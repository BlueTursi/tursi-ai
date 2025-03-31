# tursi-ai

[![GitHub release](https://img.shields.io/github/v/release/BlueTursi/tursi-ai)](https://github.com/BlueTursi/tursi-ai/releases)
[![Tests](https://github.com/BlueTursi/tursi-ai/actions/workflows/test.yml/badge.svg)](https://github.com/BlueTursi/tursi-ai/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-79%25-brightgreen.svg)](https://github.com/BlueTursi/tursi-ai)

A simple framework to deploy AI models locally with one command, no containers needed.

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

## Installation

```bash
pip install tursi
```

## Usage

```bash
# Start the server
tursi-engine up

# Test the server with curl
curl -X POST -H "Content-Type: application/json" \
     -d '{"text": "Hello, world!"}' \
     http://localhost:5000/predict
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

## Development

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

## Configuration

The following environment variables can be set:

- `RATE_LIMIT`: API rate limit (default: "100 per minute")
- `RATE_LIMIT_STORAGE_URI`: Storage backend for rate limiting (default: "memory://")

## License

[MIT License](/LICENSE)

## Acknowledgments

Built with 💙 using:
- Transformers
- Flask
- PyTorch
- Poetry

Built by [BlueTursi](https://bluetursi.com).
