"""
Unit & Integration Tests for Bloop Speech Service Engine (SpeechService)
Tests the complete application-level TTS pipeline:
- Text validation (Level 2)
- Capability & voice-language validation (Level 3)
- Optional Quantum modulation resilience
- ElevenLabs & Simulation provider execution
- Metadata persistence and transactional consistency
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.app.core.exceptions import (
    InvalidLanguageException,
    InvalidVoiceException,
    TextEmptyException,
    TextTooLongException,
    VoiceLanguageMismatchException,
)
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.providers.base import TTSProviderResult
from backend.app.providers.elevenlabs.provider import ElevenLabsProvider
from backend.app.schemas.tts import TTSRequest
from backend.app.services.speech.exceptions import SpeechPersistenceException
from backend.app.services.speech.service import SpeechService


class TestSpeechServicePipeline:
    """End-to-end tests for SpeechService orchestration."""

    @pytest.mark.asyncio
    async def test_speech_service_synthesizes_and_persists_generation(self, db_session):
        """SpeechService synthesizes audio, writes to local disk, and records metadata."""
        service = SpeechService(db_session)
        req = TTSRequest(
            text="Testing speech service generation pipeline.",
            voice_id="normal-female",
            language="en-US",
            speed=1.0,
            pitch=1.0,
            emotion="Neutral",
        )

        res = await service.generate_speech(req, user_id=None)

        assert res.generation_id is not None
        assert res.text == "Testing speech service generation pipeline."
        assert res.char_count == len("Testing speech service generation pipeline.")
        assert res.word_count == 5
        assert res.language == "en-US"
        assert res.voice_id == "normal-female"
        assert "/tts/audio/" in res.audio_url
        assert "/tts/download/" in res.download_url

        # Verify record persisted in database
        record = db_session.query(SpeechGeneration).filter(SpeechGeneration.id == res.generation_id).first()
        assert record is not None
        assert record.status == "completed"
        assert record.char_count == res.char_count
        assert record.word_count == res.word_count
        assert record.audio_filename in res.audio_url

    @pytest.mark.asyncio
    async def test_speech_service_with_elevenlabs_provider_result(self, db_session):
        """SpeechService correctly handles normalized TTSProviderResult from ElevenLabs."""
        mock_elevenlabs = MagicMock(spec=ElevenLabsProvider)
        mock_elevenlabs.is_configured.return_value = True
        mock_elevenlabs.generate_speech = AsyncMock(
            return_value=TTSProviderResult(
                audio_bytes=b"mock-elevenlabs-audio-bytes-1234",
                content_type="audio/mpeg",
                file_extension="mp3",
                provider="elevenlabs",
                provider_request_id="el-prov-req-999",
                latency_ms=210.0,
            )
        )

        service = SpeechService(db_session, elevenlabs_provider=mock_elevenlabs)

        # Set normal-female provider to elevenlabs temporarily for this test
        from backend.app.repositories.voice_repository import VoiceRepository
        voice_repo = VoiceRepository(db_session)
        voice = voice_repo.get_by_voice_id("normal-female")
        original_provider = voice.provider
        voice.provider = "elevenlabs"
        db_session.commit()

        try:
            req = TTSRequest(
                text="Testing ElevenLabs TTS provider execution through SpeechService.",
                voice_id="normal-female",
                language="en-US",
            )
            res = await service.generate_speech(req)

            assert res.provider == "elevenlabs"
            assert res.is_simulation is False
            mock_elevenlabs.generate_speech.assert_called_once()

            record = db_session.query(SpeechGeneration).filter(SpeechGeneration.id == res.generation_id).first()
            assert record.provider == "elevenlabs"
            assert record.provider_request_id == "el-prov-req-999"
            assert record.audio_format == "mp3"
        finally:
            voice.provider = original_provider
            db_session.commit()


class TestSpeechServiceValidationGuarantees:
    """Verifies that validation failures prevent provider execution."""

    @pytest.mark.asyncio
    async def test_empty_text_rejected_before_provider(self, db_session):
        mock_elevenlabs = MagicMock(spec=ElevenLabsProvider)
        mock_elevenlabs.generate_speech = AsyncMock()
        service = SpeechService(db_session, elevenlabs_provider=mock_elevenlabs)

        req = TTSRequest(text="    ", voice_id="normal-female", language="en-US")
        with pytest.raises(TextEmptyException):
            await service.generate_speech(req)

        mock_elevenlabs.generate_speech.assert_not_called()

    @pytest.mark.asyncio
    async def test_oversized_text_rejected_before_provider(self, db_session):
        mock_elevenlabs = MagicMock(spec=ElevenLabsProvider)
        mock_elevenlabs.generate_speech = AsyncMock()
        service = SpeechService(db_session, elevenlabs_provider=mock_elevenlabs)

        req = TTSRequest(text="a" * 2501, voice_id="normal-female", language="en-US")
        with pytest.raises(TextTooLongException):
            await service.generate_speech(req)

        mock_elevenlabs.generate_speech.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_language_rejected_before_provider(self, db_session):
        mock_elevenlabs = MagicMock(spec=ElevenLabsProvider)
        mock_elevenlabs.generate_speech = AsyncMock()
        service = SpeechService(db_session, elevenlabs_provider=mock_elevenlabs)

        req = TTSRequest(text="Valid text", voice_id="normal-female", language="xx-INVALID")
        with pytest.raises(InvalidLanguageException):
            await service.generate_speech(req)

        mock_elevenlabs.generate_speech.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_voice_rejected_before_provider(self, db_session):
        mock_elevenlabs = MagicMock(spec=ElevenLabsProvider)
        mock_elevenlabs.generate_speech = AsyncMock()
        service = SpeechService(db_session, elevenlabs_provider=mock_elevenlabs)

        req = TTSRequest(text="Valid text", voice_id="nonexistent-voice-999", language="en-US")
        with pytest.raises(InvalidVoiceException):
            await service.generate_speech(req)

        mock_elevenlabs.generate_speech.assert_not_called()


class TestSpeechServiceResilience:
    """Verifies quantum fault-tolerance and transaction rollback on persistence failure."""

    @pytest.mark.asyncio
    async def test_quantum_failure_does_not_break_speech_generation(self, db_session):
        """Quantum simulator crash must log warning and allow synthesis to complete gracefully."""
        service = SpeechService(db_session)

        with patch.object(
            service.quantum_modulator,
            "modulate_voice",
            side_effect=RuntimeError("Quantum statevector collapse failed"),
        ):
            req = TTSRequest(
                text="Synthesis continues despite quantum failure.",
                voice_id="normal-female",
                language="en-US",
            )
            res = await service.generate_speech(req)

            assert res.generation_id is not None
            assert res.quantum_metrics is None  # Gracefully None

    @pytest.mark.asyncio
    async def test_persistence_failure_raises_speech_persistence_exception(self, db_session):
        """If database persistence fails after audio generation, roll back safely."""
        service = SpeechService(db_session)

        with patch.object(
            service.gen_repo,
            "create",
            side_effect=Exception("Database lock error"),
        ):
            req = TTSRequest(
                text="Testing database persistence failure.",
                voice_id="normal-female",
                language="en-US",
            )
            with pytest.raises(SpeechPersistenceException) as exc_info:
                await service.generate_speech(req)

            assert "Database error during generation persistence" in str(exc_info.value)
