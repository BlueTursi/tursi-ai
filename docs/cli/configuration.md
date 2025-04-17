# Configuration Guide

This guide explains how to configure Tursi for your specific needs.

## Configuration File

Tursi uses a YAML configuration file located at `~/.config/tursi/config.yaml` by default. You can specify a different location using the `--config` flag or `TURSI_CONFIG` environment variable.

### Default Configuration

```yaml
# Server settings
server:
  host: "127.0.0.1"
  port: 8000
  workers: 1
  timeout: 30

# Model settings
model:
  default_model: "gpt2"
  cache_dir: "~/.cache/tursi"
  quantization:
    enabled: false
    bits: 8
    mode: "dynamic"

# Resource limits
limits:
  max_tokens: 2048
  rate_limit: "60/minute"
  max_concurrent_requests: 10
  max_models: 5

# Logging
logging:
  level: "INFO"
  file: "~/.local/share/tursi/tursi.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  max_size: 10485760  # 10MB
  backup_count: 5

# Security
security:
  api_key: ""  # Set this for API authentication
  allowed_origins: ["*"]
  ssl:
    enabled: false
    cert_file: ""
    key_file: ""
```

## Configuration Options

### Server Settings

- `server.host`: The IP address to bind the server to
- `server.port`: The port number for the server
- `server.workers`: Number of worker processes
- `server.timeout`: Request timeout in seconds

### Model Settings

- `model.default_model`: Default model to use if none specified
- `model.cache_dir`: Directory for storing downloaded models
- `model.quantization.enabled`: Enable model quantization
- `model.quantization.bits`: Quantization bits (4 or 8)
- `model.quantization.mode`: Quantization mode ("dynamic" or "static")

### Resource Limits

- `limits.max_tokens`: Maximum tokens per request
- `limits.rate_limit`: Rate limit in requests per time unit
- `limits.max_concurrent_requests`: Maximum simultaneous requests
- `limits.max_models`: Maximum number of loaded models

### Logging

- `logging.level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `logging.file`: Log file location
- `logging.format`: Log message format
- `logging.max_size`: Maximum log file size
- `logging.backup_count`: Number of backup log files

### Security

- `security.api_key`: API key for authentication
- `security.allowed_origins`: CORS allowed origins
- `security.ssl.enabled`: Enable SSL/TLS
- `security.ssl.cert_file`: SSL certificate file path
- `security.ssl.key_file`: SSL private key file path

## Environment Variables

All configuration options can be overridden using environment variables. The format is `TURSI_SECTION_KEY`. For example:

```bash
export TURSI_SERVER_HOST="0.0.0.0"
export TURSI_SERVER_PORT="9000"
export TURSI_MODEL_DEFAULT_MODEL="gpt2-medium"
export TURSI_LIMITS_RATE_LIMIT="100/minute"
```

## Command Line Arguments

Configuration can also be specified via command line arguments, which take precedence over both the config file and environment variables:

```bash
tursi up --host 0.0.0.0 --port 9000 --model gpt2-medium --rate-limit 100/minute
```

## Configuration Precedence

Configuration values are loaded in the following order, with later sources taking precedence:

1. Default values
2. Configuration file
3. Environment variables
4. Command line arguments

## Reloading Configuration

The configuration can be reloaded without restarting the server by sending a SIGHUP signal to the Tursi daemon:

```bash
kill -HUP $(cat /var/run/tursi/tursid.pid)
```

## Configuration Examples

### High Performance Setup

```yaml
server:
  workers: 4
  timeout: 60

model:
  quantization:
    enabled: true
    bits: 8
    mode: "dynamic"

limits:
  max_concurrent_requests: 20
  max_models: 3
```

### Development Setup

```yaml
server:
  host: "127.0.0.1"
  port: 8000
  workers: 1

logging:
  level: "DEBUG"

security:
  allowed_origins: ["http://localhost:3000"]
```

### Production Setup

```yaml
server:
  host: "0.0.0.0"
  port: 443
  workers: 8

security:
  api_key: "your-secure-api-key"
  allowed_origins: ["https://your-domain.com"]
  ssl:
    enabled: true
    cert_file: "/etc/letsencrypt/live/your-domain.com/fullchain.pem"
    key_file: "/etc/letsencrypt/live/your-domain.com/privkey.pem"

logging:
  level: "WARNING"
  file: "/var/log/tursi/tursi.log"
```
