#!/usr/bin/env python3
"""
Complete GURT Python Client Demo

This demonstrates all features of the Python GURT client library:
- Protocol message building/parsing  
- TLS 1.3 configuration
- Error handling
- Different HTTP-like methods
- Command-line usage examples

Note: This demo shows the client functionality without requiring a live server.
To test against a real GURT server, use the CLI tool or basic client examples.
"""

import sys
import os

# Add the parent directory to the path so we can import gurt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gurt import (
    GurtClient, GurtClientConfig, GurtRequest, GurtResponse, 
    GurtMethod, GurtStatusCode, GurtError, GURT_VERSION
)


def showcase_client_configuration():
    """Show different client configuration options"""
    print("=== Client Configuration Options ===")
    
    # Production configuration
    prod_config = GurtClientConfig(
        verify_tls=True,
        request_timeout=30.0,
        handshake_timeout=5.0,
        connection_timeout=10.0,
        user_agent="MyApp-GurtClient/1.0"
    )
    print("Production config:", vars(prod_config))
    
    # Development configuration  
    dev_config = GurtClientConfig(
        verify_tls=False,  # For self-signed certs
        request_timeout=60.0,  # Longer timeout for debugging
        user_agent="Dev-GurtClient/1.0"
    )
    print("Development config:", vars(dev_config))
    print()


def showcase_message_building():
    """Show how to build different types of GURT messages"""
    print("=== Message Building Examples ===")
    
    # GET request
    get_request = GurtRequest(GurtMethod.GET, "/api/users")
    get_request.with_header("Host", "api.example.gurt")
    get_request.with_header("Accept", "application/json")
    get_request.with_header("Authorization", "Bearer token123")
    
    print("GET Request:")
    print(get_request.to_bytes().decode('utf-8'))
    print()
    
    # POST request with JSON
    post_request = GurtRequest(GurtMethod.POST, "/api/users")
    post_request.with_header("Host", "api.example.gurt")
    post_request.with_header("Content-Type", "application/json")
    json_data = '{"name": "John Doe", "email": "john@example.com", "role": "user"}'
    post_request.with_body(json_data)
    
    print("POST Request with JSON:")
    print(post_request.to_bytes().decode('utf-8'))
    print()
    
    # Success response
    success_response = GurtResponse.ok()
    success_response.with_header("Content-Type", "application/json")
    response_data = '{"id": 123, "status": "created", "message": "User created successfully"}'
    success_response.with_body(response_data)
    
    print("Success Response:")
    print(success_response.to_bytes().decode('utf-8'))
    print()


def showcase_url_parsing():
    """Show URL parsing capabilities"""
    print("=== URL Parsing Examples ===")
    
    client = GurtClient()
    
    test_urls = [
        "gurt://localhost:4878/",
        "gurt://api.example.gurt/v1/users",
        "gurt://secure.site.gurt:8443/data?limit=10&offset=20",
        "gurt://127.0.0.1:4878/api/status",
    ]
    
    for url in test_urls:
        try:
            host, port, path = client._parse_gurt_url(url)
            print(f"URL: {url}")
            print(f"  Host: {host}, Port: {port}, Path: {path}")
        except GurtError as e:
            print(f"URL: {url} -> Error: {e}")
    
    print()


def showcase_error_handling():
    """Show comprehensive error handling"""
    print("=== Error Handling Examples ===")
    
    # Different types of error responses
    errors = [
        (GurtStatusCode.NOT_FOUND, "The requested resource was not found"),
        (GurtStatusCode.UNAUTHORIZED, "Authentication required"),
        (GurtStatusCode.FORBIDDEN, "Access denied"),
        (GurtStatusCode.INTERNAL_SERVER_ERROR, "Database connection failed"),
        (GurtStatusCode.BAD_GATEWAY, "Upstream server error"),
    ]
    
    for status, message in errors:
        response = GurtResponse(status)
        response.with_header("Content-Type", "application/json")
        error_data = f'{{"error": "{message}", "code": {status.value}, "timestamp": "2024-01-01T12:00:00Z"}}'
        response.with_body(error_data)
        
        print(f"{status.value} {status.message()}:")
        print(f"  Is Client Error: {response.is_client_error()}")
        print(f"  Is Server Error: {response.is_server_error()}")
        print(f"  Response Body: {response.text()}")
        print()


def showcase_practical_usage():
    """Show practical usage patterns"""
    print("=== Practical Usage Patterns ===")
    
    # This is how you would typically use the client
    print("Basic client usage pattern:")
    print("""
from gurt import GurtClient, GurtClientConfig, GurtError

# Configure client
config = GurtClientConfig(
    verify_tls=False,  # For development
    request_timeout=10.0
)
client = GurtClient(config)

try:
    # Make requests
    response = client.get("gurt://localhost:4878/api/status")
    
    if response.is_success():
        print(f"Success: {response.text()}")
        
        # Handle JSON responses
        if 'application/json' in response.get_header('content-type', ''):
            data = response.json()
            print(f"JSON: {data}")
    else:
        print(f"Error: {response.status_code} {response.status_message}")
        
except GurtError as e:
    print(f"Request failed: {e}")
""")
    
    print("\nCLI usage examples:")
    print("# Basic GET request")
    print("python3 gurt_cli.py get gurt://localhost:4878/")
    print()
    print("# POST with JSON data")
    print("python3 gurt_cli.py post gurt://localhost:4878/api/data -j '{\"key\": \"value\"}'")
    print()
    print("# With custom headers and verbose output")
    print("python3 gurt_cli.py --verbose --headers get gurt://api.example.gurt/status")
    print()
    print("# For development (disable TLS verification)")  
    print("python3 gurt_cli.py --insecure get gurt://localhost:4878/")
    print()


def main():
    """Run the complete demonstration"""
    print("GURT Python Client - Complete Feature Demonstration")
    print("=" * 60)
    print(f"Library Version: {GURT_VERSION}")
    print(f"Protocol: GURT/{GURT_VERSION} over TLS 1.3")
    print(f"Default Port: 4878")
    print()
    
    showcase_client_configuration()
    showcase_url_parsing()
    showcase_message_building()
    showcase_error_handling()
    showcase_practical_usage()
    
    print("=" * 60)
    print("Complete demonstration finished!")
    print()
    print("Next steps:")
    print("1. Set up a GURT server (see protocol/cli or protocol/library/examples)")
    print("2. Generate TLS certificates for development (see docs/gurt-protocol.md)")
    print("3. Test the Python client against your server:")
    print("   python3 gurt_cli.py --insecure get gurt://localhost:4878/")
    print()
    print("For more examples, see:")
    print("- examples/basic_client.py")
    print("- examples/advanced_client.py")
    print("- examples/protocol_demo.py")


if __name__ == "__main__":
    main()