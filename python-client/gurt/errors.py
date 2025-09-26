"""
GURT Error types
"""

class GurtError(Exception):
    """Base exception for GURT protocol errors"""
    pass

class GurtProtocolError(GurtError):
    """Raised when there's a protocol-level error"""
    pass

class GurtConnectionError(GurtError):
    """Raised when there's a connection error"""
    pass

class GurtTimeoutError(GurtError):
    """Raised when a request times out"""
    pass

class GurtTLSError(GurtError):
    """Raised when there's a TLS-related error"""
    pass

class GurtHandshakeError(GurtError):
    """Raised when the GURT handshake fails"""
    pass