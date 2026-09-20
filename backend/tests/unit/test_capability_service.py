"""
Unit tests for Bloop CapabilityService.
Validates language capability, voice availability, and language-voice compatibility.
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    InvalidLanguageException,
    InvalidVoiceException,
    VoiceLanguageMismatchException,
)
from backend.app.models.voice import Voice
from backend.app.repositories.capability_repository import CapabilityRepository
from backend.app.repositories.voice_repository import VoiceRepository
from backend.app.services.capability_service import CapabilityService


class TestCapabilityService:
    """Unit tests for centralized TTS capability resolution."""

    def test_language_and_voice_availability(self, db_session: Session):
        service = CapabilityService(db_session)
        assert service.is_language_available("en-US") is True
        assert service.is_language_available("invalid-lang") is False
        assert service.is_language_available("") is False

        assert service.is_voice_available("normal-female") is True
        assert service.is_voice_available("nonexistent-voice-999") is False
        assert service.is_voice_available("") is False

    def test_voice_language_compatibility_primary(self, db_session: Session):
        service = CapabilityService(db_session)
        # normal-female has primary language en-US
        assert service.is_voice_compatible_with_language("normal-female", "en-US") is True
        # normal-female does not natively support es-ES
        assert service.is_voice_compatible_with_language("normal-female", "es-ES") is False

    def test_multi_language_voice_capability_m2m(self, db_session: Session):
        service = CapabilityService(db_session)
        voice_repo = VoiceRepository(db_session)
        cap_repo = CapabilityRepository(db_session)

        # Retrieve test voice
        voice = voice_repo.get_by_voice_id("normal-male")
        assert voice is not None

        # Link Spanish (es-ES) as an additional supported language
        cap_repo.link_voice_language(
            voice_id=voice.id,
            language_code="es-ES",
            supported=True,
            enabled=True,
        )

        # Now normal-male supports both en-US and es-ES
        assert service.is_voice_compatible_with_language("normal-male", "en-US") is True
        assert service.is_voice_compatible_with_language("normal-male", "es-ES") is True
        assert service.is_voice_compatible_with_language("normal-male", "fr-FR") is False

        supported_langs = service.get_supported_languages_for_voice(voice)
        assert "en-US" in supported_langs
        assert "es-ES" in supported_langs

    def test_validate_tts_capability_success(self, db_session: Session):
        service = CapabilityService(db_session)
        voice, lang = service.validate_tts_capability("normal-female", "en-US")
        assert voice.voice_id == "normal-female"
        assert lang.code == "en-US"

    def test_validate_tts_capability_invalid_language_raises(self, db_session: Session):
        service = CapabilityService(db_session)
        with pytest.raises(InvalidLanguageException) as exc_info:
            service.validate_tts_capability("normal-female", "unknown-language")
        assert exc_info.value.code == "INVALID_LANGUAGE"
        assert exc_info.value.status_code == 422

    def test_validate_tts_capability_invalid_voice_raises(self, db_session: Session):
        service = CapabilityService(db_session)
        with pytest.raises(InvalidVoiceException) as exc_info:
            service.validate_tts_capability("nonexistent-voice", "en-US")
        assert exc_info.value.code == "INVALID_VOICE"
        assert exc_info.value.status_code == 422

    def test_validate_tts_capability_mismatch_raises(self, db_session: Session):
        service = CapabilityService(db_session)
        # normal-female supports en-US, requested fr-FR
        with pytest.raises(VoiceLanguageMismatchException) as exc_info:
            service.validate_tts_capability("normal-female", "fr-FR")
        assert exc_info.value.code == "VOICE_LANGUAGE_MISMATCH"
        assert exc_info.value.status_code == 422
        assert "normal-female" in str(exc_info.value.message)
        assert "fr-FR" in str(exc_info.value.message)
