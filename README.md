# tursi-ai

[![GitHub release](https://img.shields.io/github/v/release/BlueTursi/tursi-ai)](https://github.com/BlueTursi/tursi-ai/releases)

A simple, lightweight framework to deploy AI models locally with a single command—no Docker, no external services required.

## Overview

`tursi-ai` lets you run AI models (like text classification) on your machine with minimal setup. Our unique selling proposition: **"AI deployment, one command, no containers needed."** The base install is ~150-200MB, with an additional ~250MB for the default model on first run.

## Features

- **One-command deployment**: Start a model server with a single script.
- **No containers**: Runs directly in your Python environment.
- **Lightweight**: Minimal dependencies, small footprint.
- **Extensible**: Built for easy customization and growth.

## Getting Started

### Prerequisites

- Python 3.8+ (tested with 3.12)

### Installation

Install via PyPI:
```bash
pip install tursi
```

Or from source (for development)

1. Clone the repo:
```bash
git clone https://github.com/BlueTursi/tursi-ai.git
cd tursi-ai
```
2. Set up a virtual environment (required):
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. Install:
```bash
pip install .
```

## Usage

### 1. Deploy a model:
```bash
tursi-engine up
```

Stop it with:
```bash
tursi-engine down
```

Customize:
```bash
tursi-engine up --model "distilbert-base-uncased-finetuned-sst-2-english" --host "127.0.0.1" --port 8080
```

### 2. Test the deployed model:

```bash
tursi-test --prompt "I love AI"
```

Or with a custom URL:

```bash
tursi-test --prompt "I love AI" --url "http://127.0.0.1:8080/predict"
```
---

## Project Structure

```text
tursi-ai/
├── tursi/            # Core package
│   ├── engine.py     # Deployment script with CLI
│   └── test.py       # Testing utility
├── LICENSE           # MIT License
├── README.md         # This file
├── requirements.txt  # Dependencies
└── setup.py          # PyPI setup
```

## Roadmap

- Add more CLI commands (e.g., status, down).
- Support additional model types.

## Contributing
Fork this repo, make changes, and submit a PR!

## License

[MIT License](/LICENSE)

## Acknowledgments

Built with 💙 using:
- Transformers
- Flask
- PyTorch

Built by [BlueTursi](https://bluetursi.com).
