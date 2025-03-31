# tursi-ai

[![GitHub release](https://img.shields.io/github/v/release/BlueTursi/tursi-ai)](https://github.com/BlueTursi/tursi-ai/releases)

A simple framework to deploy AI models locally with one command, no containers needed.

## Features

- Deploy AI models locally with one command
- No containers needed
- Simple API interface
- Rate limiting and security features
- Automated versioning and releases

## Installation

```bash
pip install tursi
```

## Usage

```bash
# Start the server
tursi-engine up

# Test the server
tursi-test
```

## Development

```bash
# Clone the repository
git clone https://github.com/BlueTursi/tursi-ai.git
cd tursi-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Build package
python -m build
```

## License

[MIT License](/LICENSE)

## Acknowledgments

Built with 💙 using:
- Transformers
- Flask
- PyTorch

Built by [BlueTursi](https://bluetursi.com).
