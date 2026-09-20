"""
API integration tests for /api/v1/languages endpoints.
Verifies JSON envelope compliance, schema fields, and language retrieval.
"""

from fastapi.testclient import TestClient


def test_get_languages_list_contract(client: TestClient):
    response = client.get("/api/v1/languages")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0

    first = body["data"][0]
    assert "code" in first
    assert "name" in first
    assert "direction" in first
    assert first["direction"] in ("ltr", "rtl")
    assert "is_active" in first
    assert first["is_active"] is True


def test_get_single_language_success(client: TestClient):
    response = client.get("/api/v1/languages/en-US")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["code"] == "en-US"
    assert body["data"]["name"] == "English (US)"
    assert body["data"]["direction"] == "ltr"


def test_get_single_language_not_found(client: TestClient):
    response = client.get("/api/v1/languages/non-existent-lang-code")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "LANGUAGE_NOT_FOUND"
