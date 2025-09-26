#!/usr/bin/env python3
"""
Tests for GURT client URL parsing and configuration
"""

import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gurt.client import GurtClient, GurtClientConfig
from gurt.protocol import DEFAULT_PORT
from gurt.errors import GurtError


class TestGurtClient(unittest.TestCase):
    """Test GURT client functionality"""
    
    def test_client_config(self):
        """Test client configuration"""
        config = GurtClientConfig(
            handshake_timeout=10.0,
            request_timeout=60.0,
            verify_tls=False,
            user_agent="Test-Client/1.0"
        )
        
        self.assertEqual(config.handshake_timeout, 10.0)
        self.assertEqual(config.request_timeout, 60.0)
        self.assertEqual(config.verify_tls, False)
        self.assertEqual(config.user_agent, "Test-Client/1.0")
    
    def test_url_parsing(self):
        """Test GURT URL parsing"""
        client = GurtClient()
        
        # Basic URL
        host, port, path = client._parse_gurt_url("gurt://example.com/test")
        self.assertEqual(host, "example.com")
        self.assertEqual(port, DEFAULT_PORT)
        self.assertEqual(path, "/test")
        
        # URL with port
        host, port, path = client._parse_gurt_url("gurt://localhost:8080/api/data")
        self.assertEqual(host, "localhost")
        self.assertEqual(port, 8080)
        self.assertEqual(path, "/api/data")
        
        # URL with query parameters
        host, port, path = client._parse_gurt_url("gurt://api.example.com/search?q=test&limit=10")
        self.assertEqual(host, "api.example.com")
        self.assertEqual(port, DEFAULT_PORT)
        self.assertEqual(path, "/search?q=test&limit=10")
        
        # Root path
        host, port, path = client._parse_gurt_url("gurt://localhost:4878/")
        self.assertEqual(host, "localhost")
        self.assertEqual(port, 4878)
        self.assertEqual(path, "/")
        
        # No path (should default to /)
        host, port, path = client._parse_gurt_url("gurt://localhost")
        self.assertEqual(host, "localhost")
        self.assertEqual(port, DEFAULT_PORT)
        self.assertEqual(path, "/")
    
    def test_invalid_urls(self):
        """Test invalid URL handling"""
        client = GurtClient()
        
        # Wrong scheme
        with self.assertRaises(GurtError):
            client._parse_gurt_url("http://example.com/")
        
        with self.assertRaises(GurtError):
            client._parse_gurt_url("https://example.com/")
        
        # No hostname
        with self.assertRaises(GurtError):
            client._parse_gurt_url("gurt:///path")
    
    def test_ssl_context_creation(self):
        """Test SSL context creation"""
        config = GurtClientConfig(verify_tls=False)
        client = GurtClient(config)
        
        # Should create context without errors
        self.assertIsNotNone(client._ssl_context)
        
        # Should be configured for TLS 1.3
        self.assertEqual(client._ssl_context.minimum_version.name, "TLSv1_3")
        self.assertEqual(client._ssl_context.maximum_version.name, "TLSv1_3")


if __name__ == "__main__":
    unittest.main()