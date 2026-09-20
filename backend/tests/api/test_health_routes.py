"""
API Tests — Health, Liveness, and Readiness Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from backend.app.factory import create_app
from backend.app.db.session import get_db

app = create_app()
client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "data" in payload
    data = payload["data"]
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert "provider" in data
    assert "quantum" in data


def test_liveness_check_returns_200():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "alive"


def test_readiness_check_healthy_database():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ready"
    assert payload["data"]["database"] == "connected"


def test_readiness_check_failing_database():
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("Connection refused"))

    broken_app = create_app()
    broken_app.dependency_overrides[get_db] = lambda: BrokenSession()
    broken_client = TestClient(broken_app)

    response = broken_client.get("/api/v1/health/ready")
    assert response.status_code == 503
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DATABASE_UNAVAILABLE"
