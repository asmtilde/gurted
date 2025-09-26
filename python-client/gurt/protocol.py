"""
GURT Protocol constants and definitions
"""

from enum import IntEnum
from typing import Dict

# Protocol constants
GURT_VERSION = "1.0.0"
DEFAULT_PORT = 4878
PROTOCOL_PREFIX = "GURT/"

# Message separators
HEADER_SEPARATOR = "\r\n"
BODY_SEPARATOR = "\r\n\r\n"

# Timeouts (in seconds)
DEFAULT_HANDSHAKE_TIMEOUT = 5
DEFAULT_REQUEST_TIMEOUT = 30  
DEFAULT_CONNECTION_TIMEOUT = 10

# Message size limits
MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB

# TLS Configuration
GURT_ALPN = b"GURT/1.0"
TLS_VERSION = "TLS/1.3"

class GurtStatusCode(IntEnum):
    """GURT status codes compatible with HTTP semantics"""
    
    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Handshake
    SWITCHING_PROTOCOLS = 101
    
    # Client errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    TIMEOUT = 408
    TOO_LARGE = 413
    UNSUPPORTED_MEDIA_TYPE = 415
    TOO_MANY_REQUESTS = 429
    
    # Server errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

    def message(self) -> str:
        """Get the status message for this code"""
        return STATUS_MESSAGES.get(self, "UNKNOWN")
    
    def is_success(self) -> bool:
        """Check if this is a success status code"""
        return self in (self.OK, self.CREATED, self.ACCEPTED, self.NO_CONTENT)
    
    def is_client_error(self) -> bool:
        """Check if this is a client error status code"""
        return 400 <= self.value < 500
    
    def is_server_error(self) -> bool:
        """Check if this is a server error status code"""
        return self.value >= 500

# Status code messages
STATUS_MESSAGES: Dict[GurtStatusCode, str] = {
    GurtStatusCode.OK: "OK",
    GurtStatusCode.CREATED: "CREATED", 
    GurtStatusCode.ACCEPTED: "ACCEPTED",
    GurtStatusCode.NO_CONTENT: "NO_CONTENT",
    GurtStatusCode.SWITCHING_PROTOCOLS: "SWITCHING_PROTOCOLS",
    GurtStatusCode.BAD_REQUEST: "BAD_REQUEST",
    GurtStatusCode.UNAUTHORIZED: "UNAUTHORIZED",
    GurtStatusCode.FORBIDDEN: "FORBIDDEN",
    GurtStatusCode.NOT_FOUND: "NOT_FOUND",
    GurtStatusCode.METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    GurtStatusCode.TIMEOUT: "TIMEOUT",
    GurtStatusCode.TOO_LARGE: "TOO_LARGE",
    GurtStatusCode.UNSUPPORTED_MEDIA_TYPE: "UNSUPPORTED_MEDIA_TYPE",
    GurtStatusCode.TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
    GurtStatusCode.INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
    GurtStatusCode.NOT_IMPLEMENTED: "NOT_IMPLEMENTED",
    GurtStatusCode.BAD_GATEWAY: "BAD_GATEWAY",
    GurtStatusCode.SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
    GurtStatusCode.GATEWAY_TIMEOUT: "GATEWAY_TIMEOUT",
}