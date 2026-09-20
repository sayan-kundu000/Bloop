"""
Unit Tests for Centralized Error Handling & Exception Mappings
Verifies standardized JSON error envelopes, status codes, and security sanitization.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError

from backend.app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BloopException,
    ConflictException,
    DatabaseException,
    ProviderException,
    RateLimitException,
    ResourceNotFoundException,
    ServiceUnavailableException,
    ValidationException,
    register_exception_handlers,
)
from backend.app.factory import create_app


@pytest.fixture
def error_test_app():
    """Builds a test app with test endpoints that raise various exceptions."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test/validation")
    def trigger_validation():
        raise ValidationException("Invalid field value", details={"field": "voice_id"})

    @app.get("/test/auth")
    def trigger_auth():
        raise AuthenticationException("Token invalid")

    @app.get("/test/forbidden")
    def trigger_forbidden():
        raise AuthorizationException("Access denied")

    @app.get("/test/not-found")
    def trigger_not_found():
        raise ResourceNotFoundException(resource="SpeechGeneration", identifier=999)

    @app.get("/test/conflict")
    def trigger_conflict():
        raise ConflictException("Email already registered")

    @app.get("/test/rate-limit")
    def trigger_rate_limit():
        raise RateLimitException(message="Rate quota exceeded", retry_after=30)

    @app.get("/test/provider")
    def trigger_provider():
        raise ProviderException(provider="elevenlabs", message="Remote socket closed")

    @app.get("/test/database-custom")
    def trigger_database_custom():
        raise DatabaseException("Deadlock detected")

    @app.get("/test/service-unavailable")
    def trigger_service_unavailable():
        raise ServiceUnavailableException(service="quantum")

    @app.get("/test/sqlalchemy-raw")
    def trigger_sqlalchemy():
        raise OperationalError("SELECT * FROM secret_table", {}, Exception("Connection refused"))

    @app.get("/test/unhandled")
    def trigger_unhandled():
        raise ZeroDivisionError("division by zero in private code")

    class ItemModel(BaseModel):
        text: str

    @app.post("/test/pydantic-validation")
    def trigger_pydantic(item: ItemModel):
        return {"received": item.text}

    return app


class TestErrorHandling:
    """Verifies all exception mappings follow the standard JSON error contract."""

    def test_validation_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/validation")
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert body["error"]["details"]["field"] == "voice_id"

    def test_authentication_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/auth")
        assert res.status_code == 401
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_FAILED"

    def test_authorization_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/forbidden")
        assert res.status_code == 403
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "FORBIDDEN"

    def test_resource_not_found_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/not-found")
        assert res.status_code == 404
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "999" in body["error"]["message"]

    def test_conflict_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/conflict")
        assert res.status_code == 409
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "CONFLICT"

    def test_rate_limit_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/rate-limit")
        assert res.status_code == 429
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert body["error"]["details"]["retry_after_seconds"] == 30

    def test_provider_exception(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/provider")
        assert res.status_code == 502
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "PROVIDER_ERROR"
        assert "elevenlabs" in body["error"]["message"]

    def test_database_exception_sanitization(self, error_test_app):
        client = TestClient(error_test_app)
        res = client.get("/test/sqlalchemy-raw")
        assert res.status_code == 500
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "DATABASE_ERROR"
        # Verify internal SQL or table name is NOT leaked to client
        assert "secret_table" not in body["error"]["message"]

    def test_unhandled_exception_sanitization(self, error_test_app):
        client = TestClient(error_test_app, raise_server_exceptions=False)
        res = client.get("/test/unhandled")
        assert res.status_code == 500
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
        # Verify internal python exception message is NOT leaked
        assert "division by zero" not in body["error"]["message"]

    def test_pydantic_validation_error_envelope(self, error_test_app):
        client = TestClient(error_test_app)
        # Send empty payload to trigger Pydantic validation error
        res = client.post("/test/pydantic-validation", json={})
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in body["error"]
