"""
GURT Client implementation with TLS 1.3 and handshake support
"""

import socket
import ssl
import asyncio
from urllib.parse import urlparse
from typing import Optional, Tuple, Dict, Any
import logging

from .protocol import (
    DEFAULT_PORT, GURT_ALPN, TLS_VERSION,
    DEFAULT_HANDSHAKE_TIMEOUT, DEFAULT_REQUEST_TIMEOUT, DEFAULT_CONNECTION_TIMEOUT,
    MAX_MESSAGE_SIZE
)
from .message import GurtRequest, GurtResponse, GurtMethod
from .errors import (
    GurtError, GurtConnectionError, GurtTimeoutError, 
    GurtTLSError, GurtHandshakeError, GurtProtocolError
)

logger = logging.getLogger(__name__)


class GurtClientConfig:
    """Configuration for GURT client"""
    
    def __init__(
        self,
        handshake_timeout: float = DEFAULT_HANDSHAKE_TIMEOUT,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
        user_agent: str = "GURT-Python-Client/1.0.0",
        verify_tls: bool = False  # Set to False for development with self-signed certs
    ):
        self.handshake_timeout = handshake_timeout
        self.request_timeout = request_timeout
        self.connection_timeout = connection_timeout
        self.user_agent = user_agent
        self.verify_tls = verify_tls


class GurtClient:
    """GURT protocol client with TLS 1.3 support"""
    
    def __init__(self, config: Optional[GurtClientConfig] = None):
        self.config = config or GurtClientConfig()
        self._ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for TLS 1.3 with GURT ALPN"""
        try:
            context = ssl.create_default_context()
            
            # Configure for TLS 1.3
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3
            
            # Set ALPN protocols
            context.set_alpn_protocols([GURT_ALPN.decode('utf-8')])
            
            # Configure certificate verification
            if not self.config.verify_tls:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                logger.warning("TLS certificate verification disabled - only use for development!")
            
            return context
            
        except Exception as e:
            raise GurtTLSError(f"Failed to create SSL context: {e}")
    
    def _parse_gurt_url(self, url: str) -> Tuple[str, int, str]:
        """Parse a GURT URL and return (host, port, path)"""
        if not url.startswith('gurt://'):
            raise GurtError(f"URL must use gurt:// scheme: {url}")
        
        parsed = urlparse(url)
        
        if not parsed.hostname:
            raise GurtError(f"URL must have a hostname: {url}")
        
        host = parsed.hostname
        port = parsed.port or DEFAULT_PORT
        path = parsed.path or "/"
        
        if parsed.query:
            path += f"?{parsed.query}"
        
        return host, port, path
    
    def _create_connection(self, host: str, port: int) -> socket.socket:
        """Create a TCP connection to the host"""
        try:
            sock = socket.create_connection(
                (host, port), 
                timeout=self.config.connection_timeout
            )
            return sock
        except socket.timeout:
            raise GurtTimeoutError(f"Connection timeout to {host}:{port}")
        except socket.error as e:
            raise GurtConnectionError(f"Failed to connect to {host}:{port}: {e}")
    
    def _perform_handshake(self, sock: socket.socket, host: str) -> ssl.SSLSocket:
        """Perform GURT handshake and upgrade to TLS"""
        try:
            # Create handshake request
            handshake_request = GurtRequest(GurtMethod.HANDSHAKE, "/")
            handshake_request.with_header("Host", host)
            handshake_request.with_header("User-Agent", self.config.user_agent)
            
            # Send handshake request
            handshake_data = handshake_request.to_bytes()
            logger.debug(f"Sending handshake request to {host}")
            sock.sendall(handshake_data)
            
            # Read handshake response with timeout
            sock.settimeout(self.config.handshake_timeout)
            response_data = self._read_response_data(sock)
            
            # Parse handshake response
            handshake_response = GurtResponse.parse(response_data)
            
            if handshake_response.status_code != 101:  # Switching Protocols
                raise GurtHandshakeError(
                    f"Handshake failed: {handshake_response.status_code} {handshake_response.status_message}"
                )
            
            logger.debug(f"Handshake successful, upgrading to TLS")
            
            # Upgrade to TLS
            tls_sock = self._ssl_context.wrap_socket(sock, server_hostname=host)
            
            # Verify ALPN negotiation
            selected_alpn = tls_sock.selected_alpn_protocol()
            if selected_alpn != GURT_ALPN.decode('utf-8'):
                raise GurtTLSError(f"ALPN negotiation failed. Expected {GURT_ALPN}, got {selected_alpn}")
            
            logger.debug(f"TLS upgrade successful, ALPN: {selected_alpn}")
            return tls_sock
            
        except socket.timeout:
            raise GurtTimeoutError("Handshake timeout")
        except ssl.SSLError as e:
            raise GurtTLSError(f"TLS handshake failed: {e}")
        except Exception as e:
            if isinstance(e, (GurtHandshakeError, GurtTLSError, GurtTimeoutError)):
                raise
            raise GurtHandshakeError(f"Handshake failed: {e}")
    
    def _read_response_data(self, sock: socket.socket) -> bytes:
        """Read complete response data from socket"""
        data = b""
        header_end = b"\r\n\r\n"
        
        # Read until we have headers
        while header_end not in data:
            chunk = sock.recv(4096)
            if not chunk:
                raise GurtConnectionError("Connection closed while reading headers")
            data += chunk
            
            if len(data) > MAX_MESSAGE_SIZE:
                raise GurtProtocolError("Response too large")
        
        # Find end of headers
        headers_end = data.find(header_end) + len(header_end)
        headers_data = data[:headers_end]
        body_data = data[headers_end:]
        
        # Parse headers to get content-length
        headers_str = headers_data.decode('utf-8')
        content_length = 0
        
        for line in headers_str.split('\r\n'):
            if line.lower().startswith('content-length:'):
                try:
                    content_length = int(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
                break
        
        # Read remaining body data if needed
        while len(body_data) < content_length:
            chunk = sock.recv(min(4096, content_length - len(body_data)))
            if not chunk:
                raise GurtConnectionError("Connection closed while reading body")
            body_data += chunk
        
        return headers_data + body_data
    
    def _send_request_internal(self, host: str, port: int, request: GurtRequest) -> GurtResponse:
        """Send a request and return the response"""
        sock = None
        tls_sock = None
        
        try:
            # Create connection
            sock = self._create_connection(host, port)
            
            # Perform handshake and upgrade to TLS
            tls_sock = self._perform_handshake(sock, host)
            
            # Send the actual request
            request_data = request.to_bytes()
            logger.debug(f"Sending {request.method.value} request to {host}:{port}{request.path}")
            tls_sock.sendall(request_data)
            
            # Read response with timeout
            tls_sock.settimeout(self.config.request_timeout)
            response_data = self._read_response_data(tls_sock)
            
            # Parse and return response
            response = GurtResponse.parse(response_data)
            logger.debug(f"Received response: {response.status_code} {response.status_message}")
            
            return response
            
        except socket.timeout:
            raise GurtTimeoutError("Request timeout")
        except Exception as e:
            if isinstance(e, GurtError):
                raise
            raise GurtConnectionError(f"Request failed: {e}")
        finally:
            # Clean up connections
            if tls_sock:
                try:
                    tls_sock.close()
                except:
                    pass
            elif sock:
                try:
                    sock.close()
                except:
                    pass
    
    def get(self, url: str) -> GurtResponse:
        """Send a GET request"""
        host, port, path = self._parse_gurt_url(url)
        request = GurtRequest(GurtMethod.GET, path)
        request.with_header("Host", host)
        request.with_header("User-Agent", self.config.user_agent)
        
        return self._send_request_internal(host, port, request)
    
    def post(self, url: str, body: str = "", content_type: str = "text/plain") -> GurtResponse:
        """Send a POST request"""
        host, port, path = self._parse_gurt_url(url)
        request = GurtRequest(GurtMethod.POST, path)
        request.with_header("Host", host)
        request.with_header("User-Agent", self.config.user_agent)
        request.with_header("Content-Type", content_type)
        request.with_body(body)
        
        return self._send_request_internal(host, port, request)
    
    def post_json(self, url: str, data: Any) -> GurtResponse:
        """Send a POST request with JSON data"""
        import json
        json_body = json.dumps(data)
        return self.post(url, json_body, "application/json")
    
    def put(self, url: str, body: str = "", content_type: str = "text/plain") -> GurtResponse:
        """Send a PUT request"""
        host, port, path = self._parse_gurt_url(url)
        request = GurtRequest(GurtMethod.PUT, path)
        request.with_header("Host", host)
        request.with_header("User-Agent", self.config.user_agent)
        request.with_header("Content-Type", content_type)
        request.with_body(body)
        
        return self._send_request_internal(host, port, request)
    
    def delete(self, url: str) -> GurtResponse:
        """Send a DELETE request"""
        host, port, path = self._parse_gurt_url(url)
        request = GurtRequest(GurtMethod.DELETE, path)
        request.with_header("Host", host)
        request.with_header("User-Agent", self.config.user_agent)
        
        return self._send_request_internal(host, port, request)
    
    def head(self, url: str) -> GurtResponse:
        """Send a HEAD request"""
        host, port, path = self._parse_gurt_url(url)
        request = GurtRequest(GurtMethod.HEAD, path)
        request.with_header("Host", host)
        request.with_header("User-Agent", self.config.user_agent)
        
        return self._send_request_internal(host, port, request)
    
    def options(self, url: str) -> GurtResponse:
        """Send an OPTIONS request"""
        host, port, path = self._parse_gurt_url(url)
        request = GurtRequest(GurtMethod.OPTIONS, path)
        request.with_header("Host", host)
        request.with_header("User-Agent", self.config.user_agent)
        
        return self._send_request_internal(host, port, request)