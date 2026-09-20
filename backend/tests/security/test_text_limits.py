"""
Security Tests — Text Processing Limits & Provider Non-Invocation Guarantees
Verifies that malicious, excessive, or invalid text inputs never invoke TTS providers
(ElevenLabs or simulation) and that Unicode and control characters are safely handled.
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from backend.app.api.deps import get_current_user
from backend.app.core.exceptions import ErrorCode
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture(autouse=True)
def authenticate_user():
    user = User(id=1, email="test_text_limits@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


class TestProviderNonInvocationGuarantees:
    """Verifies that TTS providers are NEVER invoked on invalid text (Prompt 10 §30, §43)."""

    @patch("backend.app.services.tts_service.ElevenLabsProvider.generate_speech", new_callable=AsyncMock)
    @patch("backend.app.services.tts_service.MockTTSProvider.generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_empty_text(
        self, mock_sim_tts, mock_eleven_tts, client: TestClient
    ):
        res = client.post(
            "/api/v1/tts",
            json={"text": "", "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == ErrorCode.TEXT_EMPTY
        mock_eleven_tts.assert_not_called()
        mock_sim_tts.assert_not_called()

    @patch("backend.app.services.tts_service.ElevenLabsProvider.generate_speech", new_callable=AsyncMock)
    @patch("backend.app.services.tts_service.MockTTSProvider.generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_whitespace_only(
        self, mock_sim_tts, mock_eleven_tts, client: TestClient
    ):
        res = client.post(
            "/api/v1/tts",
            json={"text": "   \t\t\n  \r\n  ", "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == ErrorCode.TEXT_EMPTY
        mock_eleven_tts.assert_not_called()
        mock_sim_tts.assert_not_called()

    @patch("backend.app.services.tts_service.ElevenLabsProvider.generate_speech", new_callable=AsyncMock)
    @patch("backend.app.services.tts_service.MockTTSProvider.generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_oversized_text(
        self, mock_sim_tts, mock_eleven_tts, client: TestClient
    ):
        oversized = "M" * 2501
        res = client.post(
            "/api/v1/tts",
            json={"text": oversized, "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == ErrorCode.TEXT_TOO_LONG
        mock_eleven_tts.assert_not_called()
        mock_sim_tts.assert_not_called()


class TestTextSecurityAndUnicodeIntegrity:
    """Verifies security boundaries against ReDoS, control code injection, and Unicode (Prompt 10 §24, §25, §26, §44)."""

    def test_multilingual_unicode_safety(self, client: TestClient):
        # Multilingual text with Arabic, CJK, Cyrillic, accented characters, and emoji
        multilingual = (
            "Hello world! "
            "مرحبا بالعالم! "
            "こんにちは世界！ "
            "Привет мир! "
            "Bonjour le monde! "
            "Speech synthesis 🎙️✨"
        )
        res = client.post(
            "/api/v1/tts",
            json={"text": multilingual, "voice_id": "sim_voice_1", "language": "en-US"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["char_count"] == len(multilingual)
        assert data["word_count"] > 5

    def test_control_character_sanitization_security(self, client: TestClient):
        # Injection of null bytes (\x00), bells (\x07), and backspaces (\x08)
        dirty_input = "Safe text\x00 with\x07 malicious\x08 control\x0b characters."
        res = client.post(
            "/api/v1/tts",
            json={"text": dirty_input, "voice_id": "sim_voice_1", "language": "en-US"},
        )
        assert res.status_code == 200
        # Control characters stripped safely without crash
        cleaned_text = res.json()["data"]["text"]
        assert "\x00" not in cleaned_text
        assert "\x07" not in cleaned_text
        assert "\x08" not in cleaned_text
        assert "\x0b" not in cleaned_text

    def test_extremely_large_whitespace_rejection_no_redos(self, client: TestClient):
        # 5,000 spaces - tests linear O(n) performance without catastrophic regex backtracking
        huge_spaces = " " * 5000
        res = client.post(
            "/api/v1/tts",
            json={"text": huge_spaces, "voice_id": "test_voice", "language": "en-US"},
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == ErrorCode.TEXT_EMPTY
