# Installation Guide

This guide will help you install and set up Tursi on your system.

## System Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (optional, but recommended for better performance)
- At least 8GB RAM (16GB or more recommended for larger models)
- 10GB+ free disk space for model storage

## Installation Methods

### Using pip (Recommended)

```bash
pip install tursi
```

For development installation with additional tools:

```bash
pip install tursi[dev]
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tursi.git
cd tursi
```

2. Install dependencies:
```bash
pip install -e .
```

## Post-Installation Setup

1. Verify the installation:
```bash
tursi --version
```

2. Create default configuration (optional):
```bash
tursi init
```

This will create a default configuration file at `~/.config/tursi/config.yaml`.

## GPU Support

To enable GPU acceleration:

1. Install CUDA Toolkit (11.x or higher recommended)
2. Install PyTorch with CUDA support:
```bash
pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
```

## Common Issues

### CUDA Not Found

If you see "CUDA not available" warnings:
1. Verify CUDA installation: `nvidia-smi`
2. Check PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`
3. Reinstall PyTorch with the correct CUDA version if needed

### Permission Issues

If you encounter permission errors:
1. Use `--user` flag with pip: `pip install --user tursi`
2. Or create a virtual environment:
```bash
python -m venv tursi-env
source tursi-env/bin/activate  # Linux/Mac
tursi-env\Scripts\activate     # Windows
```

### Model Download Issues

If model downloads fail:
1. Check your internet connection
2. Verify you have enough disk space
3. Set custom cache directory if needed:
```bash
export TURSI_CACHE_DIR=/path/to/cache
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade tursi
```

## Uninstallation

To remove Tursi:

```bash
pip uninstall tursi
```

This will remove the package but preserve any downloaded models and configuration files.

To completely remove all Tursi data:
1. Delete the configuration directory: `~/.config/tursi/`
2. Delete the model cache (default location: `~/.cache/tursi/`)
