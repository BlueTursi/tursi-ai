# Command Reference

This document provides detailed information about each command available in the Tursi CLI.

## Model Management Commands

### `tursi up`

Start a model server for inference.

```bash
tursi up <model-name> [options]
```

**Options:**
- `--host`: Host address to bind the server (default: localhost)
- `--port`: Port number to use (default: 8000)
- `--quantize`: Enable model quantization (4-bit or 8-bit)
- `--mode`: Quantization mode (dynamic or static)
- `--rate-limit`: Set request rate limit (requests per minute)

**Examples:**
```bash
# Start a model server with default settings
tursi up gpt2

# Start with 8-bit quantization
tursi up llama2 --quantize 8 --mode dynamic

# Start on specific host and port with rate limiting
tursi up mistral --host 0.0.0.0 --port 8080 --rate-limit 100
```

### `tursi down`

Stop a running model server.

```bash
tursi down [model-name]
```

If no model name is provided, stops all running model servers.

**Examples:**
```bash
# Stop a specific model
tursi down gpt2

# Stop all running models
tursi down
```

### `tursi ps`

List all running model servers and their status.

```bash
tursi ps [options]
```

**Options:**
- `--all`: Show both running and stopped models
- `--format`: Output format (table or json)

The output includes:
- Model name
- Status (running/stopped)
- Host and port
- Uptime
- Resource usage

### `tursi logs`

View logs for a running model server.

```bash
tursi logs <model-name> [options]
```

**Options:**
- `--follow`: Stream logs in real-time
- `--tail`: Number of lines to show from the end
- `--since`: Show logs since timestamp

**Examples:**
```bash
# View last 100 lines
tursi logs gpt2 --tail 100

# Stream logs in real-time
tursi logs llama2 --follow
```

### `tursi stats`

Display resource usage statistics for running models.

```bash
tursi stats [model-name] [options]
```

**Options:**
- `--interval`: Update interval in seconds
- `--format`: Output format (table or json)

Shows:
- CPU usage
- Memory usage
- GPU utilization (if applicable)
- Request count and latency

## Global Options

These options are available for all commands:

- `--help`: Show help message for a command
- `--version`: Show Tursi version
- `--config`: Specify custom config file
- `--verbose`: Enable verbose logging
- `--quiet`: Suppress all output except errors

## Environment Variables

The following environment variables can be used to configure default behavior:

- `TURSI_HOST`: Default host address
- `TURSI_PORT`: Default port number
- `TURSI_CONFIG`: Path to config file
- `TURSI_LOG_LEVEL`: Logging level
- `TURSI_CACHE_DIR`: Model cache directory
