"""
API Tests — TTS Request Validation & Text Processing Endpoints
Verifies Level 1 (Pydantic), Level 2 (Text Processing), and Level 3 (Domain) validation
behavior on /api/v1/tts and /api/v1/tts/analyze endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.deps import get_current_user
from backend.app.core.exceptions import ErrorCode
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture(autouse=True)
def authenticate_user():
    user = User(id=1, email="test_validator@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


class TestTTSAPIValidation:
    """Tests /api/v1/tts validation pipeline and error responses."""

    def test_tts_empty_string_returns_text_empty(self, client: TestClient):
        res = client.post(
            "/api/v1/tts",
            json={"text": "", "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.TEXT_EMPTY
        assert "empty" in body["error"]["message"].lower()

    def test_tts_whitespace_only_returns_text_empty(self, client: TestClient):
        res = client.post(
            "/api/v1/tts",
            json={"text": "   \n\t  \r\n  ", "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.TEXT_EMPTY

    def test_tts_exceeding_max_characters_returns_text_too_long(self, client: TestClient):
        oversized = "X" * 2501
        res = client.post(
            "/api/v1/tts",
            json={"text": oversized, "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.TEXT_TOO_LONG
        assert body["error"]["details"]["max_characters"] == 2500
        assert body["error"]["details"]["actual_characters"] == 2501

    def test_tts_valid_text_succeeds_with_metrics(self, client: TestClient):
        text = "Valid text-to-speech synthesis request."
        res = client.post(
            "/api/v1/tts",
            json={"text": text, "voice_id": "sim_voice_1", "language": "en-US"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["char_count"] == len(text)
        assert body["data"]["word_count"] == 4
        assert body["data"]["text"] == text

    def test_tts_analyze_endpoint_metrics_and_boundaries(self, client: TestClient):
        # 1. Normal valid text
        res = client.post(
            "/api/v1/tts/analyze",
            json={"text": "Hello world from Bloop text processing engine."},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["char_count"] == 46
        assert data["word_count"] == 7
        assert data["is_valid"] is True
        assert data["error_message"] is None

        # 2. Empty text analysis
        res_empty = client.post("/api/v1/tts/analyze", json={"text": "   "})
        assert res_empty.status_code == 200
        data_empty = res_empty.json()["data"]
        assert data_empty["char_count"] == 0
        assert data_empty["word_count"] == 0
        assert data_empty["is_valid"] is False
        assert "empty" in data_empty["error_message"].lower()

        # 3. Oversized text analysis
        res_long = client.post("/api/v1/tts/analyze", json={"text": "Z" * 2505})
        assert res_long.status_code == 200
        data_long = res_long.json()["data"]
        assert data_long["char_count"] == 2505
        assert data_long["is_valid"] is False
        assert "exceeds" in data_long["error_message"].lower()
