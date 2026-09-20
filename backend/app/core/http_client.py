"""
Bloop HTTP Client Subsystem
Provides a managed, reusable HTTPX AsyncClient with connection pooling,
explicit timeouts, and clean lifecycle management.
"""

from typing import Optional
import httpx
from backend.app.core.logging import logger

# Default timeout limits for external provider communications
DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=10.0,
)

# Shared client instance (managed via FastAPI lifespan)
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """
    Returns the active reusable httpx.AsyncClient.
    If not initialized (e.g. in test contexts without lifespan), initializes a fallback client.
    """
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
    return _http_client


async def init_http_client() -> httpx.AsyncClient:
    """Initializes the application-wide HTTP client during lifespan startup."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
        logger.debug("Managed HTTP client session initialized.")
    return _http_client


async def close_http_client() -> None:
    """Safely closes the application-wide HTTP client during lifespan shutdown."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None
        logger.debug("Managed HTTP client session closed.")
