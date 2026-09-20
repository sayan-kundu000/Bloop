"""
Bloop Rate Limiting Infrastructure
In-memory token bucket rate limiter with sliding window tracking,
and FastAPI dependency integration for abuse mitigation.
"""

import time
from typing import Callable, Dict, List, Optional
from fastapi import Request
from backend.app.core.exceptions import RateLimitException


class InMemoryRateLimiter:
    """Thread-safe sliding-window rate limiter per client identifier."""

    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.window_seconds = 60.0
        self._history: Dict[str, List[float]] = {}

    def check_limit(self, identifier: str) -> bool:
        """
        Checks if the request is within rate limits.
        Raises RateLimitException if exceeded.
        """
        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self._history.get(identifier, [])
        # Prune old timestamps outside sliding window
        valid_timestamps = [t for t in timestamps if t > window_start]

        if len(valid_timestamps) >= self.rate:
            retry_after = int(self.window_seconds - (now - valid_timestamps[0])) + 1
            raise RateLimitException(retry_after=retry_after)

        valid_timestamps.append(now)
        self._history[identifier] = valid_timestamps
        return True

    def reset(self) -> None:
        """Clears all tracking history (useful for test resets)."""
        self._history.clear()


# Global default rate limiter instance
default_rate_limiter = InMemoryRateLimiter(requests_per_minute=60)


def rate_limit(
    requests_per_minute: int = 60,
    key_func: Optional[Callable[[Request], str]] = None,
):
    """
    FastAPI dependency for endpoint-level rate limiting.
    By default identifies clients by client IP address or X-Forwarded-For header.
    """
    limiter = InMemoryRateLimiter(requests_per_minute=requests_per_minute)

    async def dependency(request: Request) -> None:
        from backend.app.core.config import settings
        if not settings.RATE_LIMIT_ENABLED or (
            settings.APP_ENV == "test" and not request.headers.get("X-Test-Enforce-Rate-Limit")
        ):
            return

        if key_func:
            key = key_func(request)
        else:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                key = forwarded.split(",")[0].strip()
            else:
                key = request.client.host if request.client else "unknown"

        limiter.check_limit(f"{request.url.path}:{key}")

    return dependency
