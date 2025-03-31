# Changelog

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