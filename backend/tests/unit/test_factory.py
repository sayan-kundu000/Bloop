"""
Unit Tests for Application Factory (create_app)
Verifies application assembly, environment-aware documentation,
lifespan hooks, router mounting, and OpenAPI tag definitions.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.core.config import Settings
from backend.app.factory import create_app, OPENAPI_TAGS


class TestApplicationFactory:
    """Validates the create_app() factory function and configuration assembly."""

    def test_create_app_default_initialization(self):
        app = create_app()
        assert app.title == "Bloop AI Text-to-Speech & Quantum Intelligence API"
        assert app.openapi_tags == OPENAPI_TAGS

    def test_docs_enabled_when_debug_true(self):
        settings = Settings(
            APP_NAME="Bloop Dev",
            APP_ENV="development",
            APP_DEBUG=True,
            DATABASE_URL="sqlite:///./test_dev.db",
            JWT_SECRET_KEY="a" * 32,
        )
        app = create_app(custom_settings=settings)
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/api/v1/openapi.json"

    def test_docs_disabled_when_debug_false(self):
        settings = Settings(
            APP_NAME="Bloop Prod",
            APP_ENV="production",
            APP_DEBUG=False,
            DATABASE_URL="postgresql+psycopg://user:pass@host:5432/db",
            JWT_SECRET_KEY="a" * 32,
            CORS_ORIGINS="https://bloop.vercel.app",
        )
        app = create_app(custom_settings=settings)
        assert app.docs_url is None
        assert app.redoc_url is None
        assert app.openapi_url is None

    def test_root_endpoint_metadata(self):
        app = create_app()
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "Bloop"
        assert data["status"] == "online"
        assert data["api_v1"] == "/api/v1"

    def test_openapi_schema_generation(self):
        settings = Settings(
            APP_NAME="Bloop Test",
            APP_ENV="development",
            APP_DEBUG=True,
            DATABASE_URL="sqlite:///./test_dev.db",
            JWT_SECRET_KEY="a" * 32,
        )
        app = create_app(custom_settings=settings)
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/health" in schema["paths"]
        assert "/api/v1/auth/login" in schema["paths"]
        assert "/api/v1/users/me" in schema["paths"]
        assert "/api/v1/voices" in schema["paths"]
        assert "/api/v1/languages" in schema["paths"]
        assert "/api/v1/tts" in schema["paths"]
        assert "/api/v1/history" in schema["paths"]
        assert "/api/v1/favorites" in schema["paths"]
        assert "/api/v1/quantum/text" in schema["paths"]

        # Verify all 9 domain tags are declared in schema
        tag_names = {t["name"] for t in schema.get("tags", [])}
        expected_tags = {
            "Health", "Authentication", "Users", "Languages",
            "Voices", "Speech", "History", "Favorites", "Quantum"
        }
        assert expected_tags.issubset(tag_names)
