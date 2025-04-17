# Release Process

This document outlines the process for creating new releases of Tursi.

## 1. Prepare the Release

### 1.1 Update Version
Update the version in `pyproject.toml` according to [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for added functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

```bash
# Edit pyproject.toml
version = "X.Y.Z"  # Update this line
```

### 1.2 Update Changelog
Update `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD
### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes
```

## 2. Create Release Commit

```bash
# Stage changes
git add pyproject.toml CHANGELOG.md

# Commit with conventional commit message
git commit -m "chore(release): prepare for version X.Y.Z"

# Push changes
git push origin main
```

## 3. Create and Push Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# Push tag
git push origin vX.Y.Z
```

## 4. Monitor Release Process

1. The push of the tag will trigger the release workflow
2. The workflow will:
   - Verify version consistency
   - Run tests
   - Build package
   - Create GitHub Release
   - Publish to PyPI

## 5. Verify Release

1. Check the [GitHub Releases page](https://github.com/BlueTursi/tursi-ai/releases)
2. Verify the package is available on [PyPI](https://pypi.org/project/tursi/)
3. Test installation in a fresh virtual environment:
   ```bash
   python -m venv test-env
   source test-env/bin/activate  # or `test-env\Scripts\activate` on Windows
   pip install tursi==X.Y.Z
   ```

## Pre-release Versions

For pre-release versions, use the following format:
- Alpha: `X.Y.Z-alpha.N`
- Beta: `X.Y.Z-beta.N`
- Release Candidate: `X.Y.Z-rc.N`

Example:
```bash
# In pyproject.toml
version = "0.3.0-alpha.1"

# Tag
git tag -a v0.3.0-alpha.1 -m "Release v0.3.0-alpha.1"
```

## Hotfix Process

For urgent fixes to a release:

1. Create a hotfix branch from the release tag:
   ```bash
   git checkout -b hotfix/X.Y.Z vX.Y.Z
   ```

2. Make the necessary fixes

3. Update version and changelog

4. Create a new patch version:
   ```bash
   git tag -a vX.Y.Z+1 -m "Release vX.Y.Z+1"
   git push origin vX.Y.Z+1
   ```

## Release Checklist

- [ ] Update version in pyproject.toml
- [ ] Update CHANGELOG.md
- [ ] Commit changes
- [ ] Create and push tag
- [ ] Monitor release workflow
- [ ] Verify package on PyPI
- [ ] Test installation
- [ ] Update documentation if needed
