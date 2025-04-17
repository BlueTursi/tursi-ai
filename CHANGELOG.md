# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0-alpha.1] - 2024-04-17

### Added
- Intuitive CLI interface with `tursi up`, `tursi down`, `tursi ps`, `tursi logs`, and `tursi stats` commands
- Model quantization support (4-bit and 8-bit) for reduced memory usage
- Rate limiting for API endpoints
- Resource monitoring and statistics
- Daemon process (tursid) for managing deployments
- SQLite database for state persistence
- Automated schema migrations
- Comprehensive test suite with high coverage
- CodeCov integration for coverage reporting

### Changed
- Simplified deployment workflow for enhanced user experience
- Improved error handling and logging
- Enhanced model loading performance
- Updated documentation with more examples and best practices

### Security
- Added rate limiting by default
- Improved input validation
- Added logging for security-relevant events

## [0.2.0] - 2024-03-15

### Added
- Basic model deployment functionality
- REST API for model inference
- Support for Hugging Face models
- Initial test suite

## [0.1.0] - 2024-02-28

### Added
- Initial release
- Basic project structure
- Core model loading functionality
