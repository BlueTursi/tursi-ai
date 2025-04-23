# Contributing to Tursi-AI

Thank you for considering contributing!

## Dependency Management Best Practices

- After changing dependencies in `pyproject.toml`, always run:
  ```bash
  poetry lock
  ```
  This ensures `poetry.lock` is in sync with your changes.
- Always commit both `pyproject.toml` and `poetry.lock` together in the same PR.
- Do not manually edit `poetry.lock`.
- Use only valid, published versions for dependencies. You can check available versions with:
  ```bash
  poetry search <package>
  ```
- If your PR changes dependencies, reviewers will check that both files are updated and consistent.

## Running Tests and Linting

- Run tests locally before pushing:
  ```bash
  poetry install
  poetry run pytest
  ```
- Run linting:
  ```bash
  poetry run black --check tursi tests
  poetry run flake8 tursi tests
  poetry run mypy tursi tests
  ```

## Pull Request Guidelines

- Make sure your branch is up to date with `main` before opening a PR.
- Describe your changes clearly in the PR description.
- If your PR addresses an open issue, reference it in the description.
- Ensure all CI checks pass before requesting a review.

## Automated Dependency Updates

- This repo uses Dependabot to automate dependency updates. Review and merge these PRs promptly to keep dependencies secure and up to date.

Thank you for helping make Tursi-AI better!
