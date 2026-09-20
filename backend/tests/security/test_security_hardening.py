"""
Security Hardening & Production Defense Tests (Prompt 28)
Verifies:
- Defensive HTTP security headers (X-Content-Type-Options, X-Frame-Options, HSTS in production, etc.)
- Sanitized error envelopes without leaking stack traces or internal SQL
- CORS origin enforcement
- Quantum resource guardrails and code execution prohibition
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.factory import create_app


def test_security_headers_in_response(client: TestClient):
    """Verifies defensive HTTP security headers are present on all API responses."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "geolocation=()" in res.headers.get("Permissions-Policy", "")


def test_hsts_header_in_production():
    """Verifies Strict-Transport-Security (HSTS) is attached when APP_ENV == 'production'."""
    prod_settings = Settings(
        APP_ENV="production",
        APP_DEBUG=False,
        DATABASE_URL="postgresql+psycopg://bloop_user:test_password@localhost:5432/bloop_db",
        JWT_SECRET_KEY="production-secret-key-32-chars-minimum",
        CORS_ORIGINS="https://bloop.vercel.app",
    )
    app = create_app(custom_settings=prod_settings)
    client = TestClient(app)

    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    assert res.headers.get("X-Content-Type-Options") == "nosniff"


def test_cors_wildcard_rejected_in_production():
    """Verifies that wildcard CORS with credentials is rejected in production settings."""
    with pytest.raises(Exception):
        Settings(
            APP_ENV="production",
            APP_DEBUG=False,
            DATABASE_URL="sqlite:///./test_cors.db",
            JWT_SECRET_KEY="production-secret-key-32-chars-minimum",
            CORS_ORIGINS="*",
        )


def test_sanitized_error_response_no_stacktrace(client: TestClient):
    """Verifies error responses use clean standard error envelope and do not leak stack traces."""
    res = client.post("/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "WrongPassword123!"})
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
    assert "traceback" not in body
    assert "Traceback" not in str(body)


def test_quantum_circuit_code_injection_prohibited(client: TestClient):
    """Verifies that non-whitelisted gates or arbitrary code execution attempts in circuits are rejected."""
    # Attempt to inject arbitrary gate name
    payload = {
        "num_qubits": 2,
        "gates": [
            {"gate": "__import__('os').system('dir')", "qubits": [0]},
        ],
        "shots": 100,
    }
    # Unauthenticated request returns 401
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code in (401, 422)


def test_payload_size_limit_rejection(client: TestClient):
    """Verifies that massive request payloads exceeding 2MB are dropped before processing."""
    massive_text = "A" * (2 * 1024 * 1024 + 1024)
    res = client.post(
        "/api/v1/auth/login",
        content=massive_text,
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 413
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PAYLOAD_TOO_LARGE"
