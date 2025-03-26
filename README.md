# tursi-ai
An open-source framework to compose and deploy AI models with ease.

## Quick Start
1. Clone: `git clone https://github.com/BlueTursi/tursi-ai.git`
2. Install: `cd tursi-ai && pip install -r requirements.txt`
3. Deploy: `python tursi-engine/tursi-engine.py up --model distilbert-base-uncased-finetuned-sst-2-english`
4. Test: `curl -X POST -H "Content-Type: application/json" -d '{"text":"I love AI"}' http://localhost:5000/predict`

## Why tursi-ai?
- **Modular**: Build AI apps like blocks.
- **Simple**: Deploy with one command.
- **Local**: No external services needed.
- **Community-driven**: Join us at BlueTursi!

## Next Steps
- Add multi-model support.
- Contribute: Open an issue or PR!

Built by [BlueTursi](https://bluetursi.com).
