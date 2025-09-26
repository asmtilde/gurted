#!/usr/bin/env python3
"""
GURT Protocol Demo

This example demonstrates the GURT protocol message format and parsing
without requiring a live server connection.
"""

import sys
import os

# Add the parent directory to the path so we can import gurt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gurt import GurtRequest, GurtResponse, GurtMethod, GurtStatusCode


def demonstrate_request_building():
    """Show how GURT requests are built and formatted"""
    print("=== GURT Request Building Demo ===")
    
    # Create a GET request
    request = GurtRequest(GurtMethod.GET, "/api/status")
    request.with_header("Host", "localhost:4878")
    request.with_header("User-Agent", "GURT-Demo-Client/1.0")
    request.with_header("Accept", "application/json")
    
    print("Built GET request:")
    print(request.to_bytes().decode('utf-8'))
    print()
    
    # Create a POST request with JSON data
    json_data = '{"message": "Hello from Python GURT client!", "timestamp": "2024-01-01T12:00:00Z"}'
    
    post_request = GurtRequest(GurtMethod.POST, "/api/messages")
    post_request.with_header("Host", "api.example.gurt")
    post_request.with_header("Content-Type", "application/json")
    post_request.with_body(json_data)
    
    print("Built POST request:")
    print(post_request.to_bytes().decode('utf-8'))
    print()


def demonstrate_response_parsing():
    """Show how GURT responses are parsed"""
    print("=== GURT Response Parsing Demo ===")
    
    # Sample GURT response
    raw_response = """GURT/1.0.0 200 OK\r
Content-Type: application/json\r
Content-Length: 85\r
Server: GURT/1.0.0\r
Date: Wed, 01 Jan 2024 12:00:00 GMT\r
\r
{"status": "ok", "message": "Welcome to the Gurted network!", "server": "example.gurt"}"""
    
    # Replace literal \r with actual carriage returns
    raw_response = raw_response.replace('\\r', '\r')
    
    print("Raw response data:")
    print(repr(raw_response))
    print()
    
    # Parse the response
    response = GurtResponse.parse(raw_response)
    
    print("Parsed response:")
    print(f"Status: {response.status_code} {response.status_message}")
    print(f"Content-Type: {response.get_header('content-type')}")
    print(f"Server: {response.get_header('server')}")
    print(f"Content-Length: {response.get_header('content-length')}")
    print(f"Body: {response.text()}")
    print(f"Is Success: {response.is_success()}")
    
    # Parse as JSON
    try:
        json_data = response.json()
        print(f"JSON Data: {json_data}")
    except Exception as e:
        print(f"JSON parsing failed: {e}")
    
    print()


def demonstrate_handshake_request():
    """Show what a GURT handshake request looks like"""
    print("=== GURT Handshake Demo ===")
    
    # This is what the client sends to initiate a GURT connection
    handshake = GurtRequest(GurtMethod.HANDSHAKE, "/")
    handshake.with_header("Host", "example.gurt")
    handshake.with_header("User-Agent", "GURT-Python-Client/1.0.0")
    
    print("GURT Handshake Request:")
    print(handshake.to_bytes().decode('utf-8'))
    print()
    
    # Expected server response for successful handshake
    handshake_response = GurtResponse(GurtStatusCode.SWITCHING_PROTOCOLS)
    handshake_response.with_header("Upgrade", "GURT/1.0")
    handshake_response.with_body("")
    
    print("Expected Handshake Response:")
    print(handshake_response.to_bytes().decode('utf-8'))
    print()


def demonstrate_error_responses():
    """Show different types of error responses"""
    print("=== GURT Error Response Demo ===")
    
    # 404 Not Found
    not_found = GurtResponse(GurtStatusCode.NOT_FOUND)
    not_found.with_header("Content-Type", "text/html")
    not_found.with_body("<h1>Page Not Found</h1><p>The requested resource was not found on this server.</p>")
    
    print("404 Not Found Response:")
    print(not_found.to_bytes().decode('utf-8'))
    print()
    
    # 500 Internal Server Error with JSON
    server_error = GurtResponse(GurtStatusCode.INTERNAL_SERVER_ERROR)
    error_data = {"error": "Internal server error", "code": 500, "details": "Database connection failed"}
    server_error.with_json_body(error_data)
    
    print("500 Internal Server Error Response:")
    print(server_error.to_bytes().decode('utf-8'))
    print()


def main():
    """Run all protocol demonstrations"""
    print("GURT Protocol Format Demonstration")
    print("=" * 50)
    print()
    
    demonstrate_handshake_request()
    demonstrate_request_building()
    demonstrate_response_parsing()  
    demonstrate_error_responses()
    
    print("Protocol demonstration completed!")
    print()
    print("To test against a real GURT server, run:")
    print("  python3 gurt_cli.py --insecure get gurt://localhost:4878/")
    print()
    print("Note: Use --insecure only for development with self-signed certificates!")


if __name__ == "__main__":
    main()