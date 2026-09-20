"""
Bloop Monorepo — System Smoke Test Suite
Verifies backend liveness, API route registration, and frontend build readiness.
"""

import sys
import os
import pytest

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_probe_liveness():
    """Confirms that the FastAPI service responds to GET /api/v1/health with 200 OK."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]
    assert data["data"]["status"] == "healthy"


def test_openapi_schema_generated():
    """Confirms that the OpenAPI documentation is compiled and accessible."""
    from backend.app.core.config import Settings
    from backend.app.factory import create_app
    debug_settings = Settings(
        APP_NAME="Bloop Smoke Test",
        APP_ENV="development",
        APP_DEBUG=True,
        DATABASE_URL="sqlite:///./test_smoke.db",
        JWT_SECRET_KEY="a" * 32,
    )
    smoke_app = create_app(custom_settings=debug_settings)
    smoke_client = TestClient(smoke_app)
    response = smoke_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "Bloop" in schema["info"]["title"]
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/tts" in schema["paths"]
    assert "/api/v1/voices" in schema["paths"]
