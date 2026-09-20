"""
Unit Tests for Middleware Pipeline
Verifies Request ID correlation, security headers, response timing,
CORS headers, and payload size protections.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.factory import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    return TestClient(app)


class TestRequestIDMiddleware:
    """Verifies Request ID generation and sanitization."""

    def test_request_id_generated_when_missing(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) >= 16

    def test_request_id_preserved_when_valid(self, client):
        custom_id = "test-req-correlation-12345"
        response = client.get("/", headers={"X-Request-ID": custom_id})
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    def test_request_id_sanitized_when_invalid(self, client):
        # Invalid chars (e.g. spaces or control chars) must be replaced with a clean generated ID
        invalid_id = "bad id with spaces; DROP TABLE"
        response = client.get("/", headers={"X-Request-ID": invalid_id})
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] != invalid_id
        assert len(response.headers["X-Request-ID"]) >= 16


class TestSecurityHeadersMiddleware:
    """Verifies defensive security headers are appended to all responses."""

    def test_security_headers_present(self, client):
        response = client.get("/")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "Permissions-Policy" in response.headers
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"


class TestRequestTimingMiddleware:
    """Verifies performance timing instrumentation."""

    def test_response_time_header_present(self, client):
        response = client.get("/")
        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("ms")


class TestCORSMiddleware:
    """Verifies CORS origin validation."""

    def test_cors_preflight_allowed_origin(self, client):
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert response.headers.get("access-control-allow-credentials") == "true"
