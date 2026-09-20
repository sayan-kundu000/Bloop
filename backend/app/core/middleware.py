"""
Bloop Core Middleware Pipeline
Provides an ordered, robust middleware architecture for FastAPI:
1. CORS Middleware (Environment-driven allowed origins)
2. Request ID Correlation (Tracing & Observability)
3. Security Headers (HSTS, MIME-sniffing, Framing protection)
4. Request Timing & Access Logging (Performance & Observability)
5. Request Payload Limit Protection
"""

import re
import time
import uuid
from typing import Callable, Optional
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import Settings, settings as global_settings
from backend.app.core.logging import logger

# Maximum allowed Content-Length (2MB default for text/speech metadata payloads)
MAX_CONTENT_LENGTH_BYTES = 2 * 1024 * 1024
SAFE_REQUEST_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Extracts or generates a correlation Request ID for tracing and observability.
    Validates client-supplied X-Request-ID to prevent header injection.
    Attaches the ID to request.state.request_id and response headers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_request_id = request.headers.get("X-Request-ID")
        if client_request_id and SAFE_REQUEST_ID_REGEX.match(client_request_id):
            request_id = client_request_id
        else:
            request_id = uuid.uuid4().hex

        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies defensive security headers to all HTTP responses.
    Mitigates clickjacking, MIME-type sniffing, and unintended cross-origin leaks.
    In production environments, strictly enforces HSTS (HTTP Strict Transport Security).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Production HSTS enforcement
        app_settings = getattr(request.app.state, "settings", None)
        env = getattr(app_settings, "APP_ENV", "development") if app_settings else "development"
        if env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Measures and logs request processing duration.
    Attaches X-Response-Time header to the response.
    Emits structured, sanitized access logs without exposing sensitive bodies or auth tokens.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", "unknown")

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        # Log request summary safely
        # Paths like /health can be logged at DEBUG to avoid flood, others at INFO
        if request.url.path in ("/api/v1/health/live", "/health/live"):
            log_fn = logger.debug
        else:
            log_fn = logger.info

        log_fn(
            f"HTTP {request.method} {request.url.path} "
            f"returned {response.status_code} in {duration_ms:.2f}ms "
            f"[request_id={request_id}]"
        )
        return response


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    """
    Protects backend services from oversized request payloads (e.g., massive text flood).
    Rejects requests exceeding MAX_CONTENT_LENGTH_BYTES before parsing into memory.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > MAX_CONTENT_LENGTH_BYTES:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "error": {
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": f"Request payload exceeds maximum allowed size of {MAX_CONTENT_LENGTH_BYTES} bytes.",
                                "details": {"max_bytes": MAX_CONTENT_LENGTH_BYTES, "received_bytes": length},
                            },
                        },
                    )
            except ValueError:
                pass

        return await call_next(request)


def register_middleware(app: FastAPI, settings: Optional[Settings] = None) -> None:
    """
    Registers the full middleware pipeline onto the FastAPI application in correct order.
    Starlette executes middleware in reverse order of addition:
    Last added = First to execute on Request / Last to execute on Response.
    
    Order of execution on incoming request:
    1. CORS Middleware (evaluates origin & preflights first)
    2. Payload Limit Middleware (drops oversized requests early)
    3. Request ID Middleware (establishes request_id for downstream)
    4. Security Headers Middleware
    5. Request Timing Middleware (measures time through downstream application)
    """
    cfg = settings or global_settings

    # Added in reverse execution order:
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(PayloadLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )
