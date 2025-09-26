#!/usr/bin/env python3
"""
Advanced GURT Client Example

This example shows more advanced usage of the GURT Python client.
"""

import sys
import os
import json

# Add the parent directory to the path so we can import gurt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gurt import GurtClient, GurtClientConfig, GurtError, GurtMethod
from gurt.message import GurtRequest


def custom_request_example():
    """Example of building custom requests"""
    print("=== Custom Request Example ===")
    
    config = GurtClientConfig(verify_tls=False)
    client = GurtClient(config)
    
    try:
        # Build a custom request
        request = GurtRequest(GurtMethod.GET, "/api/custom")
        request.with_header("X-Custom-Header", "MyValue")
        request.with_header("Accept", "application/json")
        
        # You would typically send this through internal methods,
        # but for demonstration, let's use the standard client methods
        response = client.get("gurt://localhost:4878/api/custom")
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text()}")
        
    except GurtError as e:
        print(f"Custom request failed: {e}")
    
    print()


def upload_file_example():
    """Example of uploading a file via PUT"""
    print("=== File Upload Example ===")
    
    config = GurtClientConfig(verify_tls=False)
    client = GurtClient(config)
    
    try:
        # Create some sample content
        file_content = "This is sample file content from Python GURT client."
        
        response = client.put(
            "gurt://localhost:4878/api/files/sample.txt",
            body=file_content,
            content_type="text/plain"
        )
        
        print(f"Upload Status: {response.status_code} {response.status_message}")
        if response.is_success():
            print("File uploaded successfully!")
        else:
            print(f"Upload failed: {response.text()}")
            
    except GurtError as e:
        print(f"File upload failed: {e}")
    
    print()


def batch_requests_example():
    """Example of making multiple requests"""
    print("=== Batch Requests Example ===")
    
    config = GurtClientConfig(verify_tls=False, request_timeout=5.0)
    client = GurtClient(config)
    
    endpoints = [
        "gurt://localhost:4878/",
        "gurt://localhost:4878/api/status", 
        "gurt://localhost:4878/api/info",
        "gurt://localhost:4878/health"
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            print(f"Requesting {endpoint}...")
            response = client.get(endpoint)
            results.append({
                "url": endpoint,
                "status": response.status_code,
                "success": response.is_success(),
                "response_length": len(response.body)
            })
            print(f"  -> {response.status_code} {response.status_message}")
            
        except GurtError as e:
            results.append({
                "url": endpoint,
                "status": None,
                "success": False,
                "error": str(e)
            })
            print(f"  -> Error: {e}")
    
    print("\nBatch Results Summary:")
    successful = sum(1 for r in results if r.get("success", False))
    print(f"Successful requests: {successful}/{len(results)}")
    
    print()


def api_interaction_example():
    """Example of interacting with a REST API"""
    print("=== API Interaction Example ===")
    
    config = GurtClientConfig(verify_tls=False)
    client = GurtClient(config)
    
    try:
        # Create a resource
        print("Creating a new resource...")
        create_data = {
            "name": "Python Test Resource",
            "description": "Created by GURT Python client",
            "data": {"key": "value", "number": 42}
        }
        
        response = client.post_json("gurt://localhost:4878/api/resources", create_data)
        print(f"Create Status: {response.status_code}")
        
        if response.is_success():
            try:
                created_resource = response.json()
                resource_id = created_resource.get("id")
                print(f"Created resource with ID: {resource_id}")
                
                # Read the resource back
                if resource_id:
                    print(f"Reading resource {resource_id}...")
                    response = client.get(f"gurt://localhost:4878/api/resources/{resource_id}")
                    print(f"Read Status: {response.status_code}")
                    
                    if response.is_success():
                        resource_data = response.json()
                        print(f"Resource data: {json.dumps(resource_data, indent=2)}")
                    
                    # Update the resource
                    print(f"Updating resource {resource_id}...")
                    update_data = {"description": "Updated by Python client"}
                    response = client.put(
                        f"gurt://localhost:4878/api/resources/{resource_id}",
                        json.dumps(update_data),
                        "application/json"
                    )
                    print(f"Update Status: {response.status_code}")
                    
                    # Delete the resource
                    print(f"Deleting resource {resource_id}...")
                    response = client.delete(f"gurt://localhost:4878/api/resources/{resource_id}")
                    print(f"Delete Status: {response.status_code}")
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
        else:
            print(f"Failed to create resource: {response.text()}")
            
    except GurtError as e:
        print(f"API interaction failed: {e}")
    
    print()


def main():
    """Run all advanced examples"""
    print("GURT Python Client - Advanced Examples")
    print("=" * 50)
    
    custom_request_example()
    upload_file_example()
    batch_requests_example()
    api_interaction_example()
    
    print("All examples completed!")


if __name__ == "__main__":
    main()