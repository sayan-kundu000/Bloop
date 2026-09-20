"""
Security & Credential Isolation Tests for Bloop TTS Engine (Prompt 14 §81, §82, §84)
Verifies:
- ELEVENLABS_API_KEY is never leaked to clients, logs, or exception traces.
- Unauthenticated requests to POST /api/v1/tts are rejected with HTTP 401.
- Provider isolation: ElevenLabs synthesis is NEVER invoked for unauthenticated or unauthorized requests.
- Rate limiting protects against quota abuse.
- Path traversal is strictly mitigated.
"""

import logging
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.logging import SecretMaskingFilter
from backend.app.core.security import create_access_token
from backend.app.models.user import User


@pytest.fixture
def auth_headers(db_session):
    """Provides valid JWT Bearer credentials for TTS security tests."""
    user = db_session.query(User).filter(User.email == "tts_sec_user@bloop.ai").first()
    if not user:
        user = User(
            email="tts_sec_user@bloop.ai",
            hashed_password="hash-tts-security-12345",
            full_name="TTS Security Tester",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


class TestCredentialIsolationAndSecurity:
    """Verifies that ElevenLabs API key never leaks through any layer."""

    def test_api_key_not_in_settings_representation(self):
        secret = "test-secret-key-1234567890abcdef"
        with patch.object(settings, "ELEVENLABS_API_KEY", secret):
            repr_str = repr(settings)
            assert secret not in repr_str
            assert "***" in repr_str

    def test_api_key_scrubbed_from_log_records(self):
        secret = "el_live_supersecrettoken987654321"
        masker = SecretMaskingFilter([secret])

        record = logging.LogRecord(
            name="bloop.elevenlabs",
            level=logging.ERROR,
            pathname=__file__,
            lineno=20,
            msg=f"ElevenLabs error with secret key {secret} present in trace.",
            args=(),
            exc_info=None,
        )
        assert masker.filter(record) is True
        assert secret not in record.msg
        assert "***MASKED***" in record.msg

    def test_api_key_never_in_tts_response(self, client: TestClient, auth_headers):
        secret = "el_live_confidential_key_to_protect"
        with patch.object(settings, "ELEVENLABS_API_KEY", secret):
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Checking for confidential key leakage.",
                    "voice_id": "normal-female",
                    "language": "en-US",
                },
                headers=auth_headers,
            )
            assert res.status_code == 200
            content = res.text
            assert secret not in content

    def test_api_key_never_in_exception_body(self, client: TestClient, auth_headers):
        secret = "el_live_confidential_key_to_protect"
        with patch.object(settings, "ELEVENLABS_API_KEY", secret):
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Checking for error leakage.",
                    "voice_id": "invalid-voice-id",
                    "language": "en-US",
                },
                headers=auth_headers,
            )
            assert res.status_code == 422
            assert secret not in res.text


class TestProviderIsolationAndAuth:
    """Verifies that unauthorized requests never reach external ElevenLabs provider (Prompt 14 §81, §82)."""

    def test_unauthenticated_request_never_calls_elevenlabs(self, client: TestClient):
        with patch("backend.app.providers.elevenlabs.provider.ElevenLabsProvider.generate_speech", new_callable=AsyncMock) as mock_synth:
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Unauthorized synthesis request that must be blocked.",
                    "voice_id": "normal-female",
                    "language": "en-US",
                },
            )
            assert res.status_code == 401
            assert res.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
            mock_synth.assert_not_called()

    def test_authenticated_request_allows_synthesis(self, client: TestClient, auth_headers):
        res = client.post(
            "/api/v1/tts",
            json={
                "text": "Authorized synthesis request for legitimate user.",
                "voice_id": "normal-female",
                "language": "en-US",
            },
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert res.json()["success"] is True


class TestRateLimitingAndPathTraversal:
    """Verifies rate limiting defense and file system path traversal mitigations."""

    def test_rate_limiting_enforced_when_quota_exceeded(self, client: TestClient, auth_headers):
        """When rate limiting is enforced, exceeding quota returns HTTP 429."""
        headers = {**auth_headers, "X-Test-Enforce-Rate-Limit": "true"}

        # TTS endpoint limit is 10/min
        hit_429 = False
        for _ in range(15):
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Rate limit quota test text.",
                    "voice_id": "normal-female",
                    "language": "en-US",
                },
                headers=headers,
            )
            if res.status_code == 429:
                hit_429 = True
                data = res.json()
                assert data["success"] is False
                assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
                break

        assert hit_429 is True

    def test_audio_path_traversal_protection(self, client: TestClient, auth_headers):
        """Path traversal sequences in audio streaming must not escape storage and return 404."""
        res = client.get("/api/v1/tts/audio/%2E%2E%2Fetc%2Fpasswd", headers=auth_headers)
        assert res.status_code == 404
        assert res.json()["error"]["code"] in ("RESOURCE_NOT_FOUND", "HTTP_404")

    def test_download_path_traversal_protection(self, client: TestClient, auth_headers):
        """Path traversal sequences in audio download must not escape storage and return 404."""
        res = client.get("/api/v1/tts/download/%2E%2E%2Fwindows%2Fcmd.exe", headers=auth_headers)
        assert res.status_code == 404
        assert res.json()["error"]["code"] in ("RESOURCE_NOT_FOUND", "HTTP_404")
