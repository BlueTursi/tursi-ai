# Tursi AI v0.3.0-alpha.1

Deploy AI models with unmatched simplicity - zero container overhead. This release introduces a streamlined deployment workflow with powerful optimization features designed for resource-constrained environments.

## 🚀 Highlights

- **Intuitive CLI**: Simple commands - `tursi up`, `tursi down`, `tursi ps`, `tursi logs`, `tursi stats`
- **Edge-Optimized**: 4-bit and 8-bit quantization for minimal memory footprint
- **Process Management**: Lightweight daemon (`tursid`) for reliable deployments
- **Resource Monitoring**: Real-time CPU and memory tracking
- **Enhanced Security**: Built-in rate limiting and improved error handling

## 🔧 Installation

```bash
pip install tursi==0.3.0-alpha.1
```

## 🎯 Quick Start

```bash
# Deploy a model
tursi up distilbert-base-uncased --port 8000 --quantization dynamic --bits 4

# List running models
tursi ps

# Monitor resources
tursi stats
```

## 📝 Breaking Changes

- `deploy` command replaced with `up` for improved consistency
- Updated configuration format
- New environment variables for customization

## 📚 Documentation

Full documentation and release notes: [RELEASE_NOTES.md](RELEASE_NOTES.md)

## 🐛 Bug Fixes

- Fixed memory leaks in long-running deployments
- Resolved process management race conditions
- Improved error handling
- Fixed metrics collection accuracy

## 🤝 Support

- Issues: [GitHub Issues](https://github.com/BlueTursi/tursi-ai/issues)
- Docs: [Documentation](https://tursi.readthedocs.io/)
- Community: [Discord](https://discord.gg/tursi)
