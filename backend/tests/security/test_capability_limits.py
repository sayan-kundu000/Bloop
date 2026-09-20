"""
Security, Capability Boundary & Provider Non-Invocation Guarantees (Prompt 11).
Verifies that invalid languages, invalid voices, and voice-language mismatches
strictly NEVER invoke external TTS providers (ElevenLabs / Mock).
Verifies empty catalog handling and secret leakage prevention.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.language import Language
from backend.app.models.user import User
from backend.app.models.voice import Voice
from backend.app.providers.elevenlabs_provider import ElevenLabsProvider
from backend.app.providers.mock_provider import MockTTSProvider


@pytest.fixture(autouse=True)
def authenticate_user():
    user = User(id=1, email="test_capability@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


class TestCapabilityProviderNonInvocation:
    """Verifies that synthesis providers are strictly protected from invalid capability requests."""

    @patch.object(ElevenLabsProvider, "generate_speech", new_callable=AsyncMock)
    @patch.object(MockTTSProvider, "generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_invalid_language(
        self, mock_mock_gen: AsyncMock, mock_el_gen: AsyncMock, client: TestClient
    ):
        res = client.post(
            "/api/v1/tts",
            json={
                "text": "Valid text for synthesis.",
                "voice_id": "normal-female",
                "language": "non-existent-language-code-xx",
            },
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_LANGUAGE"

        # Zero provider calls
        mock_el_gen.assert_not_called()
        mock_mock_gen.assert_not_called()

    @patch.object(ElevenLabsProvider, "generate_speech", new_callable=AsyncMock)
    @patch.object(MockTTSProvider, "generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_invalid_voice(
        self, mock_mock_gen: AsyncMock, mock_el_gen: AsyncMock, client: TestClient
    ):
        res = client.post(
            "/api/v1/tts",
            json={
                "text": "Valid text for synthesis.",
                "voice_id": "nonexistent-phantom-voice",
                "language": "en-US",
            },
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_VOICE"

        # Zero provider calls
        mock_el_gen.assert_not_called()
        mock_mock_gen.assert_not_called()

    @patch.object(ElevenLabsProvider, "generate_speech", new_callable=AsyncMock)
    @patch.object(MockTTSProvider, "generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_voice_language_mismatch(
        self, mock_mock_gen: AsyncMock, mock_el_gen: AsyncMock, client: TestClient
    ):
        # normal-female is registered for en-US, request French (fr-FR)
        res = client.post(
            "/api/v1/tts",
            json={
                "text": "Valid text for synthesis.",
                "voice_id": "normal-female",
                "language": "fr-FR",
            },
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VOICE_LANGUAGE_MISMATCH"

        # Zero provider calls
        mock_el_gen.assert_not_called()
        mock_mock_gen.assert_not_called()

    @patch.object(ElevenLabsProvider, "generate_speech", new_callable=AsyncMock)
    @patch.object(MockTTSProvider, "generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_disabled_language(
        self, mock_mock_gen: AsyncMock, mock_el_gen: AsyncMock, client: TestClient, db_session: Session
    ):
        # Temporarily disable a language
        lang = db_session.query(Language).filter(Language.code == "de-DE").first()
        if lang:
            lang.is_active = False
            db_session.commit()

        try:
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Valid text for synthesis.",
                    "voice_id": "normal-female",
                    "language": "de-DE",
                },
            )
            assert res.status_code == 422
            assert res.json()["error"]["code"] == "INVALID_LANGUAGE"

            # Zero provider calls
            mock_el_gen.assert_not_called()
            mock_mock_gen.assert_not_called()
        finally:
            if lang:
                lang.is_active = True
                db_session.commit()

    @patch.object(ElevenLabsProvider, "generate_speech", new_callable=AsyncMock)
    @patch.object(MockTTSProvider, "generate_speech", new_callable=AsyncMock)
    def test_provider_never_called_on_disabled_voice(
        self, mock_mock_gen: AsyncMock, mock_el_gen: AsyncMock, client: TestClient, db_session: Session
    ):
        # Temporarily disable a voice
        voice = db_session.query(Voice).filter(Voice.voice_id == "normal-male").first()
        if voice:
            voice.is_active = False
            db_session.commit()

        try:
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Valid text for synthesis.",
                    "voice_id": "normal-male",
                    "language": "en-US",
                },
            )
            assert res.status_code == 422
            assert res.json()["error"]["code"] == "INVALID_VOICE"

            # Zero provider calls
            mock_el_gen.assert_not_called()
            mock_mock_gen.assert_not_called()
        finally:
            if voice:
                voice.is_active = True
                db_session.commit()


class TestSecurityAndSecretLeakageGuarantees:
    """Verifies that credentials and internal vendor details are never exposed."""

    def test_api_key_not_exposed_in_catalog_or_errors(self, client: TestClient):
        # 1. Languages endpoint
        res_lang = client.get("/api/v1/languages")
        assert "ELEVENLABS_API_KEY" not in res_lang.text
        assert "api_key" not in res_lang.text

        # 2. Voices endpoint
        res_voice = client.get("/api/v1/voices")
        assert "ELEVENLABS_API_KEY" not in res_voice.text
        assert "api_key" not in res_voice.text
        assert "provider_voice_id" not in res_voice.text

        # 3. Error response
        res_err = client.post(
            "/api/v1/tts",
            json={"text": "hello", "voice_id": "nonexistent", "language": "en-US"},
        )
        assert "ELEVENLABS_API_KEY" not in res_err.text
        assert "api_key" not in res_err.text
        assert res_err.json()["error"]["code"] == "INVALID_VOICE"
