# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning Strategy

This project follows semantic versioning with the following rules:
- Breaking changes trigger a major version bump (X.0.0)
- New features trigger a minor version bump (0.X.0)
- Bug fixes and documentation updates trigger a patch version bump (0.0.X)

Only breaking changes and new features will trigger a GitHub release and PyPI publication.
Patch updates will only update the version number and changelog.

## [0.2.1] - 2024-03-31

### Security
- Fixed critical RCE vulnerability by updating PyTorch to >=2.3.2
- Added rate limiting to prevent API abuse
- Added input validation and sanitization
- Added model name whitelist
- Disabled debug mode in production
- Added secure logging
- Added environment variable support for sensitive configuration

### Added
- Rate limiting with Flask-Limiter
- Input validation with maximum length limit
- Model name sanitization
- Environment variable configuration
- Improved error handling and logging

### Changed
- Updated PyTorch dependency to >=2.3.2
- Added new security-related dependencies (python-dotenv, cryptography)
- Improved error messages for better security
- Forced CPU-only inference for better security

### Fixed
- Critical RCE vulnerability in PyTorch
- Potential information leakage in error messages
- Debug mode security issues 