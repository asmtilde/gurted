#!/usr/bin/env python3
"""
Tests for GURT message parsing and building
"""

import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gurt.message import GurtRequest, GurtResponse, GurtMethod
from gurt.protocol import GurtStatusCode, GURT_VERSION
from gurt.errors import GurtProtocolError


class TestGurtRequest(unittest.TestCase):
    """Test GURT request parsing and building"""
    
    def test_request_building(self):
        """Test building a GURT request"""
        request = GurtRequest(GurtMethod.GET, "/test")
        request.with_header("Host", "example.com")
        request.with_header("Accept", "text/html")
        request.with_body("test body")
        
        # Check properties
        self.assertEqual(request.method, GurtMethod.GET)
        self.assertEqual(request.path, "/test")
        self.assertEqual(request.version, GURT_VERSION)
        self.assertEqual(request.get_header("host"), "example.com")
        self.assertEqual(request.get_header("accept"), "text/html")
        self.assertEqual(request.text(), "test body")
    
    def test_request_to_bytes(self):
        """Test converting request to bytes"""
        request = GurtRequest(GurtMethod.POST, "/api/data")
        request.with_header("Host", "localhost")
        request.with_header("Content-Type", "application/json")
        request.with_body('{"test": true}')
        
        data = request.to_bytes()
        self.assertIsInstance(data, bytes)
        
        # Should contain the request line
        data_str = data.decode('utf-8')
        self.assertIn(f"POST /api/data GURT/{GURT_VERSION}", data_str)
        self.assertIn("host: localhost", data_str)
        self.assertIn("content-type: application/json", data_str)
        self.assertIn('{"test": true}', data_str)
    
    def test_request_parsing(self):
        """Test parsing a GURT request"""
        raw_request = f"GET /test GURT/{GURT_VERSION}\r\nHost: example.com\r\nAccept: text/html\r\n\r\ntest body"
        
        request = GurtRequest.parse(raw_request)
        
        self.assertEqual(request.method, GurtMethod.GET)
        self.assertEqual(request.path, "/test")
        self.assertEqual(request.version, GURT_VERSION)
        self.assertEqual(request.get_header("host"), "example.com")
        self.assertEqual(request.get_header("accept"), "text/html")
        self.assertEqual(request.text(), "test body")
    
    def test_request_parsing_invalid(self):
        """Test parsing invalid requests"""
        with self.assertRaises(GurtProtocolError):
            GurtRequest.parse("INVALID REQUEST")
        
        with self.assertRaises(GurtProtocolError):
            GurtRequest.parse("GET /test HTTP/1.1\r\n\r\n")  # Wrong protocol


class TestGurtResponse(unittest.TestCase):
    """Test GURT response parsing and building"""
    
    def test_response_building(self):
        """Test building a GURT response"""
        response = GurtResponse.ok()
        response.with_header("Content-Type", "text/html")
        response.with_body("<html></html>")
        
        self.assertEqual(response.status_code, GurtStatusCode.OK)
        self.assertEqual(response.get_header("content-type"), "text/html")
        self.assertEqual(response.text(), "<html></html>")
        self.assertTrue(response.is_success())
    
    def test_response_json(self):
        """Test JSON response handling"""
        data = {"message": "Hello", "success": True}
        response = GurtResponse.ok().with_json_body(data)
        
        self.assertEqual(response.get_header("content-type"), "application/json")
        parsed_data = response.json()
        self.assertEqual(parsed_data, data)
    
    def test_response_to_bytes(self):
        """Test converting response to bytes"""
        response = GurtResponse(GurtStatusCode.CREATED)
        response.with_header("Location", "/api/resource/123")
        response.with_body("Resource created")
        
        data = response.to_bytes()
        self.assertIsInstance(data, bytes)
        
        data_str = data.decode('utf-8')
        self.assertIn(f"GURT/{GURT_VERSION} 201 CREATED", data_str)
        self.assertIn("location: /api/resource/123", data_str)
        self.assertIn("Resource created", data_str)
    
    def test_response_parsing(self):
        """Test parsing a GURT response"""
        raw_response = f"GURT/{GURT_VERSION} 200 OK\r\nContent-Type: text/html\r\n\r\n<html></html>"
        
        response = GurtResponse.parse(raw_response)
        
        self.assertEqual(response.status_code, GurtStatusCode.OK)
        self.assertEqual(response.status_message, "OK")
        self.assertEqual(response.get_header("content-type"), "text/html")
        self.assertEqual(response.text(), "<html></html>")
        self.assertTrue(response.is_success())
    
    def test_status_code_methods(self):
        """Test status code helper methods"""
        # Success
        response = GurtResponse.ok()
        self.assertTrue(response.is_success())
        self.assertFalse(response.is_client_error())
        self.assertFalse(response.is_server_error())
        
        # Client error
        response = GurtResponse.not_found()
        self.assertFalse(response.is_success())
        self.assertTrue(response.is_client_error())
        self.assertFalse(response.is_server_error())
        
        # Server error
        response = GurtResponse.internal_server_error()
        self.assertFalse(response.is_success())
        self.assertFalse(response.is_client_error())
        self.assertTrue(response.is_server_error())


if __name__ == "__main__":
    unittest.main()