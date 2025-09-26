#!/usr/bin/env python3
"""
Basic GURT Client Example

This example shows how to use the GURT Python client to connect to Gurted network servers.
"""

import sys
import os

# Add the parent directory to the path so we can import gurt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gurt import GurtClient, GurtClientConfig, GurtError


def main():
    """Basic client usage example"""
    
    # Create client configuration
    # For development with self-signed certificates, disable TLS verification
    config = GurtClientConfig(
        verify_tls=False,  # Only for development!
        request_timeout=10.0,
        user_agent="GURT-Example-Client/1.0"
    )
    
    # Create client
    client = GurtClient(config)
    
    # Example 1: Simple GET request
    print("=== Example 1: GET Request ===")
    try:
        response = client.get("gurt://localhost:4878/")
        print(f"Status: {response.status_code} {response.status_message}")
        print(f"Content-Type: {response.get_header('content-type')}")
        print(f"Body: {response.text()}")
        print()
    except GurtError as e:
        print(f"GET request failed: {e}")
        print()
    
    # Example 2: POST request with JSON data
    print("=== Example 2: POST Request with JSON ===")
    try:
        data = {"message": "Hello from Python GURT client!", "timestamp": "2024-01-01T00:00:00Z"}
        response = client.post_json("gurt://localhost:4878/api/messages", data)
        print(f"Status: {response.status_code} {response.status_message}")
        if response.is_success():
            print(f"Response: {response.text()}")
        print()
    except GurtError as e:
        print(f"POST request failed: {e}")
        print()
    
    # Example 3: GET request to a different endpoint
    print("=== Example 3: GET API Endpoint ===")
    try:
        response = client.get("gurt://localhost:4878/api/status")
        print(f"Status: {response.status_code} {response.status_message}")
        
        # Check if response is JSON
        content_type = response.get_header('content-type')
        if content_type and 'application/json' in content_type:
            try:
                json_data = response.json()
                print(f"JSON Response: {json_data}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
        else:
            print(f"Text Response: {response.text()}")
        print()
    except GurtError as e:
        print(f"API request failed: {e}")
        print()
    
    # Example 4: Error handling
    print("=== Example 4: Error Handling ===")
    try:
        response = client.get("gurt://localhost:4878/nonexistent")
        print(f"Status: {response.status_code} {response.status_message}")
        
        if response.is_client_error():
            print("This is a client error (4xx)")
        elif response.is_server_error():
            print("This is a server error (5xx)")
        elif response.is_success():
            print("Request was successful (2xx)")
            
    except GurtError as e:
        print(f"Request failed with error: {e}")


if __name__ == "__main__":
    main()