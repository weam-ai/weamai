"""
Transport-aware OAuth callback handling.

In streamable-http mode: Uses the existing FastAPI server
In stdio mode: Starts a minimal HTTP server just for OAuth callbacks
"""

import os
import asyncio
import logging
import threading
import time
import socket
import uvicorn

from fastapi import FastAPI, Request
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MinimalOAuthServer:
    """
    Minimal HTTP server for OAuth callbacks in stdio mode.
    Only starts when needed and uses the same port (8000) as streamable-http mode.
    """

    def __init__(self, port: int = 8000, base_uri: str = "http://localhost"):
        self.port = port
        self.base_uri = base_uri
        self.app = FastAPI()
        self.server = None
        self.server_thread = None
        self.is_running = False

        # Setup the callback route
        self._setup_callback_route()

    def start(self) -> bool:
        """
        Start the minimal OAuth server.

        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running:
            logger.info("Minimal OAuth server is already running")
            return True

        # Check if port is available
        # Extract hostname from base_uri (e.g., "http://localhost" -> "localhost")
        try:
            parsed_uri = urlparse(self.base_uri)
            hostname = parsed_uri.hostname or 'localhost'
        except Exception:
            hostname = 'localhost'

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((hostname, self.port))
        except OSError:
            logger.error(f"Port {self.port} is already in use on {hostname}. Cannot start minimal OAuth server.")
            return False

        def run_server():
            """Run the server in a separate thread."""
            try:
                config = uvicorn.Config(
                    self.app,
                    host=hostname,
                    port=self.port,
                    log_level="warning",
                    access_log=False
                )
                self.server = uvicorn.Server(config)
                asyncio.run(self.server.serve())

            except Exception as e:
                logger.error(f"Minimal OAuth server error: {e}", exc_info=True)

        # Start server in background thread
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # Wait for server to start
        max_wait = 3.0
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    result = s.connect_ex((hostname, self.port))
                    if result == 0:
                        self.is_running = True
                        logger.info(f"Minimal OAuth server started on {hostname}:{self.port}")
                        return True
            except Exception:
                pass
            time.sleep(0.1)

        logger.error(f"Failed to start minimal OAuth server on {hostname}:{self.port}")
        return False

    def stop(self):
        """Stop the minimal OAuth server."""
        if not self.is_running:
            return

        try:
            if self.server:
                if hasattr(self.server, 'should_exit'):
                    self.server.should_exit = True

            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=3.0)

            self.is_running = False
            logger.info("Minimal OAuth server stopped")

        except Exception as e:
            logger.error(f"Error stopping minimal OAuth server: {e}", exc_info=True)


# Global instance for stdio mode
_minimal_oauth_server: Optional[MinimalOAuthServer] = None

def get_oauth_redirect_uri(port: int = 8000, base_uri: str = "http://localhost") -> str:
    """
    Get the appropriate OAuth redirect URI.

    Priority:
    1. GOOGLE_OAUTH_REDIRECT_URI environment variable
    2. Constructed from port and base URI

    Args:
        port: Port number (default 8000)
        base_uri: Base URI (default "http://localhost")

    Returns:
        OAuth redirect URI
    """
    # Highest priority: Use the environment variable if it's set
    env_redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
    if env_redirect_uri:
        logger.info(f"Using redirect URI from GOOGLE_OAUTH_REDIRECT_URI: {env_redirect_uri}")
        return env_redirect_uri

    # Fallback to constructing the URI based on server settings
    constructed_uri = f"{base_uri}:{port}/oauth2callback"
    logger.info(f"Constructed redirect URI: {constructed_uri}")
    return constructed_uri

def ensure_oauth_callback_available(transport_mode: str = "stdio", port: int = 8000, base_uri: str = "http://localhost") -> bool:
    """
    Ensure OAuth callback endpoint is available for the given transport mode.

    For streamable-http: Assumes the main server is already running
    For stdio: Starts a minimal server if needed

    Args:
        transport_mode: "stdio" or "streamable-http"
        port: Port number (default 8000)
        base_uri: Base URI (default "http://localhost")

    Returns:
        True if callback endpoint is available, False otherwise
    """
    global _minimal_oauth_server

    if transport_mode == "streamable-http":
        # In streamable-http mode, the main FastAPI server should handle callbacks
        logger.debug("Using existing FastAPI server for OAuth callbacks (streamable-http mode)")
        return True

    elif transport_mode == "stdio":
        # In stdio mode, start minimal server if not already running
        if _minimal_oauth_server is None:
            logger.info(f"Creating minimal OAuth server instance for {base_uri}:{port}")
            _minimal_oauth_server = MinimalOAuthServer(port, base_uri)

        if not _minimal_oauth_server.is_running:
            logger.info("Starting minimal OAuth server for stdio mode")
            result = _minimal_oauth_server.start()
            if result:
                logger.info(f"Minimal OAuth server successfully started on {base_uri}:{port}")
            else:
                logger.error(f"Failed to start minimal OAuth server on {base_uri}:{port}")
            return result
        else:
            logger.info("Minimal OAuth server is already running")
            return True

    else:
        logger.error(f"Unknown transport mode: {transport_mode}")
        return False

def cleanup_oauth_callback_server():
    """Clean up the minimal OAuth server if it was started."""
    global _minimal_oauth_server
    if _minimal_oauth_server:
        _minimal_oauth_server.stop()
        _minimal_oauth_server = None