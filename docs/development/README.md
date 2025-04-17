# Development Guide

This guide provides information for developers contributing to Tursi.

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/BlueTursi/tursi-ai.git
cd tursi-ai
```

2. Install Poetry (if not installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

## Development Workflow

1. Create a new branch for your feature/fix:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure tests pass:
```bash
poetry run pytest
```

3. Format code and check style:
```bash
poetry run black .
poetry run flake8
```

4. Commit your changes following conventional commits:
```bash
git commit -m "feat: add new feature"
```

## Building the Package

1. Clean up old builds before creating new ones:
```bash
# Remove old build artifacts
rm -rf dist/
mkdir -p dist/
```

2. Build the package:
```bash
poetry build
```

This will create both wheel and source distribution in the `dist/` directory.

**Important:** Always clean the `dist/` directory before building to avoid accumulating old versions. The cleanup step is automatically handled in CI/CD, but should be done manually during local development.

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=tursi

# Run specific test file
poetry run pytest tests/test_specific.py
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality. Install them with:

```bash
poetry run pre-commit install
```

## Documentation

1. Build documentation locally:
```bash
cd docs
make html
```

2. View documentation:
```bash
python -m http.server -d _build/html
```

## Release Process

1. Update version:
```bash
python scripts/bump_version.py [major|minor|patch]
```

2. Update CHANGELOG.md with your changes

3. Create and push a tag:
```bash
git tag -a v0.3.0 -m "Release v0.3.0"
git push origin v0.3.0
```

For more details on releases, see [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## Troubleshooting

### Common Issues

1. **Poetry environment issues**
   ```bash
   poetry env remove python
   poetry install
   ```

2. **Test database issues**
   ```bash
   rm -rf tests/test.db
   ```

3. **Cache issues**
   ```bash
   rm -rf .pytest_cache
   rm -rf .coverage
   ```

## Getting Help

- Check the [troubleshooting guide](../troubleshooting.md)
- Open an issue on GitHub
- Join our Discord community
