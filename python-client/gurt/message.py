"""
GURT Message types - Request and Response parsing and building
"""

from enum import Enum
from typing import Dict, Optional, Union
from datetime import datetime, timezone
import json

from .protocol import (
    GURT_VERSION, PROTOCOL_PREFIX, HEADER_SEPARATOR, BODY_SEPARATOR,
    GurtStatusCode, STATUS_MESSAGES
)
from .errors import GurtProtocolError


class GurtMethod(Enum):
    """GURT request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    HANDSHAKE = "HANDSHAKE"


class GurtRequest:
    """GURT protocol request"""
    
    def __init__(self, method: GurtMethod, path: str, version: str = GURT_VERSION):
        self.method = method
        self.path = path
        self.version = version
        self.headers: Dict[str, str] = {}
        self.body: bytes = b""
    
    def with_header(self, key: str, value: str) -> 'GurtRequest':
        """Add a header to the request"""
        self.headers[key.lower()] = value
        return self
    
    def with_body(self, body: Union[str, bytes]) -> 'GurtRequest':
        """Set the request body"""
        if isinstance(body, str):
            self.body = body.encode('utf-8')
        else:
            self.body = body
        return self
    
    def get_header(self, key: str) -> Optional[str]:
        """Get a header value (case-insensitive)"""
        return self.headers.get(key.lower())
    
    def text(self) -> str:
        """Get the body as text"""
        return self.body.decode('utf-8')
    
    def to_bytes(self) -> bytes:
        """Convert request to bytes for transmission"""
        # Status line
        message = f"{self.method.value} {self.path} {PROTOCOL_PREFIX}{self.version}{HEADER_SEPARATOR}"
        
        # Add default headers
        headers = self.headers.copy()
        if 'content-length' not in headers:
            headers['content-length'] = str(len(self.body))
        if 'user-agent' not in headers:
            headers['user-agent'] = f"GURT-Python-Client/{GURT_VERSION}"
        
        # Add headers
        for key, value in headers.items():
            message += f"{key}: {value}{HEADER_SEPARATOR}"
        
        # End headers
        message += HEADER_SEPARATOR
        
        # Convert to bytes and add body
        message_bytes = message.encode('utf-8')
        message_bytes += self.body
        
        return message_bytes
    
    @classmethod
    def parse(cls, data: Union[str, bytes]) -> 'GurtRequest':
        """Parse a GURT request from raw data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Find body separator
        body_sep = BODY_SEPARATOR.encode('utf-8')
        if body_sep in data:
            headers_part, body_part = data.split(body_sep, 1)
        else:
            headers_part, body_part = data, b""
        
        # Parse headers section
        headers_str = headers_part.decode('utf-8')
        lines = headers_str.split(HEADER_SEPARATOR)
        
        if not lines:
            raise GurtProtocolError("Empty request")
        
        # Parse request line
        request_line = lines[0]
        parts = request_line.split()
        
        if len(parts) != 3:
            raise GurtProtocolError("Invalid request line format")
        
        # Parse method
        try:
            method = GurtMethod(parts[0])
        except ValueError:
            raise GurtProtocolError(f"Unsupported method: {parts[0]}")
        
        path = parts[1]
        
        # Parse version
        if not parts[2].startswith(PROTOCOL_PREFIX):
            raise GurtProtocolError("Invalid protocol identifier")
        
        version = parts[2][len(PROTOCOL_PREFIX):]
        
        # Create request
        request = cls(method, path, version)
        request.body = body_part
        
        # Parse headers
        for line in lines[1:]:
            if not line.strip():
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                request.headers[key.strip().lower()] = value.strip()
        
        return request


class GurtResponse:
    """GURT protocol response"""
    
    def __init__(self, status_code: GurtStatusCode, version: str = GURT_VERSION):
        self.version = version
        self.status_code = status_code
        self.status_message = status_code.message()
        self.headers: Dict[str, str] = {}
        self.body: bytes = b""
    
    @classmethod
    def ok(cls) -> 'GurtResponse':
        """Create a 200 OK response"""
        return cls(GurtStatusCode.OK)
    
    @classmethod
    def not_found(cls) -> 'GurtResponse':
        """Create a 404 Not Found response"""
        return cls(GurtStatusCode.NOT_FOUND)
    
    @classmethod
    def bad_request(cls) -> 'GurtResponse':
        """Create a 400 Bad Request response"""
        return cls(GurtStatusCode.BAD_REQUEST)
        
    @classmethod
    def internal_server_error(cls) -> 'GurtResponse':
        """Create a 500 Internal Server Error response"""
        return cls(GurtStatusCode.INTERNAL_SERVER_ERROR)
    
    def with_header(self, key: str, value: str) -> 'GurtResponse':
        """Add a header to the response"""
        self.headers[key.lower()] = value
        return self
    
    def with_body(self, body: Union[str, bytes]) -> 'GurtResponse':
        """Set the response body"""
        if isinstance(body, str):
            self.body = body.encode('utf-8')
        else:
            self.body = body
        return self
    
    def with_json_body(self, data) -> 'GurtResponse':
        """Set the response body as JSON"""
        json_str = json.dumps(data)
        self.body = json_str.encode('utf-8')
        self.headers['content-type'] = 'application/json'
        return self
    
    def get_header(self, key: str) -> Optional[str]:
        """Get a header value (case-insensitive)"""
        return self.headers.get(key.lower())
    
    def text(self) -> str:
        """Get the body as text"""
        return self.body.decode('utf-8')
    
    def json(self):
        """Parse the body as JSON"""
        return json.loads(self.body.decode('utf-8'))
    
    def is_success(self) -> bool:
        """Check if this is a success response"""
        return self.status_code.is_success()
    
    def is_client_error(self) -> bool:
        """Check if this is a client error response"""
        return self.status_code.is_client_error()
    
    def is_server_error(self) -> bool:
        """Check if this is a server error response"""
        return self.status_code.is_server_error()
    
    def to_bytes(self) -> bytes:
        """Convert response to bytes for transmission"""
        # Status line
        message = f"{PROTOCOL_PREFIX}{self.version} {self.status_code.value} {self.status_message}{HEADER_SEPARATOR}"
        
        # Add default headers
        headers = self.headers.copy()
        if 'content-length' not in headers:
            headers['content-length'] = str(len(self.body))
        if 'server' not in headers:
            headers['server'] = f"GURT/{GURT_VERSION}"
        if 'date' not in headers:
            headers['date'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Add headers
        for key, value in headers.items():
            message += f"{key}: {value}{HEADER_SEPARATOR}"
        
        # End headers
        message += HEADER_SEPARATOR
        
        # Convert to bytes and add body
        message_bytes = message.encode('utf-8')
        message_bytes += self.body
        
        return message_bytes
    
    @classmethod
    def parse(cls, data: Union[str, bytes]) -> 'GurtResponse':
        """Parse a GURT response from raw data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Find body separator
        body_sep = BODY_SEPARATOR.encode('utf-8')
        if body_sep in data:
            headers_part, body_part = data.split(body_sep, 1)
        else:
            headers_part, body_part = data, b""
        
        # Parse headers section
        headers_str = headers_part.decode('utf-8')
        lines = headers_str.split(HEADER_SEPARATOR)
        
        if not lines:
            raise GurtProtocolError("Empty response")
        
        # Parse status line
        status_line = lines[0]
        parts = status_line.split(' ', 2)
        
        if len(parts) < 2:
            raise GurtProtocolError("Invalid status line format")
        
        # Parse version
        if not parts[0].startswith(PROTOCOL_PREFIX):
            raise GurtProtocolError("Invalid protocol identifier")
        
        version = parts[0][len(PROTOCOL_PREFIX):]
        
        # Parse status code
        try:
            status_code = GurtStatusCode(int(parts[1]))
        except (ValueError, KeyError):
            raise GurtProtocolError(f"Invalid status code: {parts[1]}")
        
        # Create response
        response = cls(status_code, version)
        response.body = body_part
        
        # Override status message if provided
        if len(parts) > 2:
            response.status_message = parts[2]
        
        # Parse headers
        for line in lines[1:]:
            if not line.strip():
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                response.headers[key.strip().lower()] = value.strip()
        
        return response