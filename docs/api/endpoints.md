# API Reference

This document describes the REST API endpoints provided by the Tursi server.

## Authentication

When API authentication is enabled, include your API key in the request header:

```
Authorization: Bearer your-api-key
```

## Base URL

By default, the API is available at:

```
http://localhost:8000/api/v1
```

## Endpoints

### Model Management

#### List Available Models

```http
GET /models
```

Lists all available models and their status.

**Response**
```json
{
  "models": [
    {
      "name": "gpt2",
      "status": "loaded",
      "quantized": true,
      "memory_usage": "500MB",
      "uptime": "2h 30m"
    },
    {
      "name": "gpt2-medium",
      "status": "not_loaded"
    }
  ]
}
```

#### Load Model

```http
POST /models/{model_name}/load
```

Loads a model into memory.

**Parameters**
```json
{
  "quantize": true,
  "bits": 8,
  "mode": "dynamic"
}
```

**Response**
```json
{
  "status": "loading",
  "message": "Model loading initiated",
  "estimated_time": "30s"
}
```

#### Unload Model

```http
POST /models/{model_name}/unload
```

Unloads a model from memory.

**Response**
```json
{
  "status": "success",
  "message": "Model unloaded successfully"
}
```

### Text Generation

#### Generate Text

```http
POST /generate
```

Generates text using the specified model.

**Parameters**
```json
{
  "model": "gpt2",
  "prompt": "Once upon a time",
  "max_tokens": 100,
  "temperature": 0.7,
  "top_p": 0.9,
  "stop": ["\n\n", "THE END"],
  "stream": false
}
```

**Response**
```json
{
  "text": "Once upon a time in a distant galaxy...",
  "tokens_generated": 20,
  "generation_time": "1.2s"
}
```

#### Stream Generation

For streaming responses, set `stream: true` in the request. The response will be a stream of server-sent events:

```http
event: text
data: {"text": "Once", "finished": false}

event: text
data: {"text": " upon", "finished": false}

event: text
data: {"text": " a", "finished": false}

event: done
data: {"tokens_generated": 20, "generation_time": "1.2s"}
```

### Server Status

#### Get Server Status

```http
GET /status
```

Returns the current server status and resource usage.

**Response**
```json
{
  "status": "healthy",
  "uptime": "24h 12m",
  "active_models": 2,
  "memory_usage": {
    "total": "8GB",
    "used": "6GB",
    "free": "2GB"
  },
  "gpu_usage": {
    "total": "8GB",
    "used": "4GB",
    "free": "4GB",
    "utilization": "60%"
  },
  "requests": {
    "total": 1000,
    "success": 980,
    "failed": 20,
    "rate": "10/minute"
  }
}
```

#### Get Model Metrics

```http
GET /models/{model_name}/metrics
```

Returns detailed metrics for a specific model.

**Response**
```json
{
  "name": "gpt2",
  "metrics": {
    "requests_total": 500,
    "tokens_generated": 50000,
    "average_generation_time": "1.5s",
    "memory_usage": "500MB",
    "load_time": "2023-04-01T12:00:00Z",
    "error_rate": "0.1%"
  }
}
```

### Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

```json
{
  "error": {
    "code": "model_not_found",
    "message": "The requested model 'gpt3' was not found",
    "details": {
      "available_models": ["gpt2", "gpt2-medium"]
    }
  }
}
```

Common status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1682668800
```

## Versioning

The API version is included in the URL path (/api/v1). Breaking changes will result in a new API version.

## Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Generate text
response = requests.post(
    f"{API_URL}/generate",
    headers=headers,
    json={
        "model": "gpt2",
        "prompt": "Once upon a time",
        "max_tokens": 100
    }
)
print(response.json()["text"])

# Stream generation
response = requests.post(
    f"{API_URL}/generate",
    headers=headers,
    json={
        "model": "gpt2",
        "prompt": "Once upon a time",
        "max_tokens": 100,
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode())
```

### cURL

```bash
# Generate text
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt2",
    "prompt": "Once upon a time",
    "max_tokens": 100
  }'

# Get server status
curl "http://localhost:8000/api/v1/status" \
  -H "Authorization: Bearer your-api-key"
```
