# tursi-ai

A simple, lightweight framework to deploy AI models locally with a single command—no Docker, no external services required.

## Overview

`tursi-ai` lets you run AI models (like text classification) on your machine with minimal setup. Our unique selling proposition: **"AI deployment, one command, no containers needed."** The base install is ~150-200MB, with an additional ~250MB for the default model on first run. Perfect for developers who want simplicity without complexity.

## Features

- **One-command deployment**: Start a model server with a single script.
- **No containers**: Runs directly in your Python environment.
- **Lightweight**: Minimal dependencies, small footprint.
- **Extensible**: Built for easy customization and growth.

## Getting Started

### Prerequisites

- Python 3.8+ (tested with 3.12)
- A virtual environment (recommended)

### Installation

1. **Clone or download this project** (for now, until PyPI packaging):
   ```bash
   git clone <path-to-your-local-repo>  # Or copy the folder manually
   cd tursi-ai
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   This installs everything needed for both `tursi-engine` and `tursi-test`.

### Usage

1. **Deploy a model**:
   Run the engine to start a Flask server with the default model (`distilbert-base-uncased-finetuned-sst-2-english`):
   ```bash
   python tursi-engine/tursi-engine.py
   ```
   Output:
   ```
   Loading model...
   Model loaded!
   Deploying at http://localhost:5000/predict
   ```

2. **Test the deployed model**:
   Use the included `tursi-test` script to send a prompt to the server. In a separate terminal (with the virtual environment activated):
   ```bash
   python tursi-test/tursi-test.py --prompt "I love AI"
   ```
   Expected output:
   ```json
   {
     "label": "POSITIVE",
     "score": 0.999...
   }
   ```

   Alternatively, test with `curl`:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"text":"I love AI"}' http://localhost:5000/predict
   ```

## Project Structure

```
tursi-ai/
├── .github/          # GitHub Actions (e.g., linting)
├── examples/         # Sample configs (future use)
├── tursi-engine/     # Core deployment script
├── tursi-test/       # Testing utility
├── LICENSE           # MIT License
├── README.md         # This file
├── requirements.txt  # Dependencies
└── .gitignore        # Git ignore rules
```

## Roadmap

- Add CLI support (e.g., `tursi-engine up --model <model-name>`).
- Package as a PyPI module (`pip install tursi`).
- Support more model types beyond text classification.

## Contributing

This is an open-source project under the MIT License. Feel free to fork, tweak, or submit ideas! For now, the repo is local—stay tuned for a public release.

## License

MIT License—see [LICENSE](./LICENSE) for details.

## Acknowledgments

Built with ❤️ using:
- [Transformers](https://huggingface.co/transformers) by Hugging Face
- [Flask](https://flask.palletsprojects.com/)
- [PyTorch](https://pytorch.org/)

Built by [BlueTursi](https://bluetursi.com).
