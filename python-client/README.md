# GURT Python Client

A Python implementation of the GURT protocol client for connecting to the Gurted network.

## Overview

The GURT protocol is a TCP-based protocol with mandatory TLS 1.3 encryption, designed for the Gurted ecosystem. This Python client allows you to connect to GURT servers and make HTTP-like requests with enhanced security.

## Features

- **TLS 1.3 Mandatory**: All connections use TLS 1.3 with proper ALPN negotiation
- **GURT Handshake**: Implements the GURT handshake protocol for connection establishment
- **HTTP-like Interface**: Familiar methods (GET, POST, PUT, DELETE, HEAD, OPTIONS)
- **JSON Support**: Built-in JSON serialization/deserialization
- **Error Handling**: Comprehensive error handling with specific exception types
- **Configurable**: Timeout settings, TLS verification, and more
- **Command-line Tool**: Includes a CLI tool for testing GURT connections

## Installation

Since this is part of the Gurted repository, you can use it directly:

```bash
# Navigate to the python-client directory
cd python-client

# Run examples
python3 examples/basic_client.py

# Use the CLI tool
python3 gurt_cli.py get gurt://localhost:4878/
```

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Quick Start

### Basic Usage

```python
from gurt import GurtClient, GurtClientConfig

# Create client with configuration
config = GurtClientConfig(
    verify_tls=False,  # For development with self-signed certs
    request_timeout=10.0
)
client = GurtClient(config)

# Make a GET request
response = client.get("gurt://localhost:4878/")
print(f"Status: {response.status_code}")
print(f"Body: {response.text()}")

# Make a POST request with JSON
data = {"message": "Hello, Gurted!"}
response = client.post_json("gurt://localhost:4878/api/data", data)
```

### Command Line Usage

```bash
# GET request
python3 gurt_cli.py get gurt://localhost:4878/

# POST request with JSON data
python3 gurt_cli.py post gurt://localhost:4878/api/data -j '{"key": "value"}'

# POST request with file
python3 gurt_cli.py post gurt://localhost:4878/upload -f myfile.txt

# Show headers and enable verbose logging
python3 gurt_cli.py --headers --verbose get gurt://localhost:4878/api/status
```

## API Reference

### GurtClient

The main client class for making GURT requests.

```python
client = GurtClient(config=None)
```

#### Methods

- `get(url)` - Send GET request
- `post(url, body="", content_type="text/plain")` - Send POST request  
- `post_json(url, data)` - Send POST request with JSON data
- `put(url, body="", content_type="text/plain")` - Send PUT request
- `delete(url)` - Send DELETE request
- `head(url)` - Send HEAD request
- `options(url)` - Send OPTIONS request

### GurtClientConfig

Configuration class for the client.

```python
config = GurtClientConfig(
    handshake_timeout=5.0,      # Handshake timeout in seconds
    request_timeout=30.0,       # Request timeout in seconds  
    connection_timeout=10.0,    # Connection timeout in seconds
    user_agent="GURT-Python-Client/1.0.0",  # User agent string
    verify_tls=True            # Enable TLS certificate verification
)
```

### GurtResponse

Response object returned by client methods.

#### Properties

- `status_code` - HTTP-like status code
- `status_message` - Status message string
- `headers` - Dictionary of response headers
- `body` - Raw response body as bytes

#### Methods

- `text()` - Get body as UTF-8 string
- `json()` - Parse body as JSON
- `get_header(key)` - Get header value (case-insensitive)
- `is_success()` - Check if status code indicates success (2xx)
- `is_client_error()` - Check if status code indicates client error (4xx)
- `is_server_error()` - Check if status code indicates server error (5xx)

## Error Handling

The client raises specific exceptions for different error conditions:

- `GurtError` - Base exception for all GURT errors
- `GurtConnectionError` - Connection-related errors
- `GurtTimeoutError` - Timeout errors
- `GurtTLSError` - TLS-related errors  
- `GurtHandshakeError` - GURT handshake failures
- `GurtProtocolError` - Protocol parsing errors

```python
from gurt import GurtClient, GurtError, GurtTimeoutError

client = GurtClient()

try:
    response = client.get("gurt://example.com/")
except GurtTimeoutError:
    print("Request timed out")
except GurtError as e:
    print(f"GURT error: {e}")
```

## Examples

See the `examples/` directory for complete examples:

- `basic_client.py` - Basic usage examples
- `advanced_client.py` - Advanced usage patterns

## Protocol Details

This client implements the GURT protocol as specified in the Gurted documentation:

- **URL Scheme**: `gurt://host:port/path`
- **Default Port**: 4878
- **TLS Version**: TLS 1.3 (mandatory)
- **ALPN Protocol**: `GURT/1.0`
- **Handshake**: Custom GURT handshake before TLS upgrade

## Development

For development with self-signed certificates (common in local testing), disable TLS verification:

```python
config = GurtClientConfig(verify_tls=False)
client = GurtClient(config)
```

**Warning**: Never disable TLS verification in production environments.

## License

This is part of the Gurted project. See the main repository LICENSE file for details.