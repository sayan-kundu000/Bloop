"""
Bloop Centralized TTS Capability Resolution Service
Authoritative engine for resolving language support, provider capabilities,
voice availability, and voice-to-language compatibility.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    InvalidLanguageException,
    InvalidVoiceException,
    VoiceLanguageMismatchException,
)
from backend.app.models.language import Language
from backend.app.models.voice import Voice
from backend.app.repositories.capability_repository import CapabilityRepository
from backend.app.repositories.language_repository import LanguageRepository
from backend.app.repositories.voice_repository import VoiceRepository


class CapabilityService:
    """
    Centralized Capability Resolution Engine.
    Enforces that invalid languages, voices, or incompatible combinations
    are rejected prior to any provider invocation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.lang_repo = LanguageRepository(db)
        self.voice_repo = VoiceRepository(db)
        self.capability_repo = CapabilityRepository(db)

    # -------------------------------------------------------------------------
    # Language Capability Checks
    # -------------------------------------------------------------------------

    def is_language_available(self, language_code: str) -> bool:
        """Determines if a language exists and is enabled in Bloop."""
        if not language_code or not language_code.strip():
            return False
        lang = self.lang_repo.get_by_code(language_code.strip())
        return bool(lang and lang.is_active)

    def is_provider_capable(self, provider: str, language_code: str) -> bool:
        """
        Checks whether an external provider supports a language and Bloop enables it.
        If no explicit ProviderCapability record exists, defaults to True if language is active.
        """
        if not language_code or not provider:
            return False
        cap = self.capability_repo.get_provider_capability(provider, language_code.strip())
        if cap:
            return bool(cap.supported and cap.enabled)
        # Default fallback: if language is active in Bloop, treat as capable
        return self.is_language_available(language_code)

    # -------------------------------------------------------------------------
    # Voice Capability Checks
    # -------------------------------------------------------------------------

    def is_voice_available(self, voice_id: str) -> bool:
        """Determines if a voice exists and is enabled in Bloop."""
        if not voice_id or not voice_id.strip():
            return False
        voice = self.voice_repo.get_by_voice_id(voice_id.strip())
        return bool(voice and voice.is_active)

    def get_supported_languages_for_voice(self, voice: Voice) -> List[str]:
        """
        Returns all language codes supported by this voice.
        Combines the primary language_code with any active M2M mappings.
        """
        languages = set()
        if voice.language_code:
            languages.add(voice.language_code)

        m2m_caps = self.capability_repo.list_voice_language_capabilities(voice.id, enabled_only=True)
        for cap in m2m_caps:
            languages.add(cap.language_code)

        return sorted(list(languages))

    def is_voice_compatible_with_language(self, voice_id: str, language_code: str) -> bool:
        """
        Verifies if a voice can speak the requested language.
        Checks primary voice language and M2M capability links.
        """
        if not voice_id or not language_code:
            return False

        target_lang = language_code.strip()
        voice = self.voice_repo.get_by_voice_id(voice_id.strip())
        if not voice or not voice.is_active:
            return False

        if voice.language_code == target_lang:
            return True

        # Check M2M capability link
        m2m_cap = self.capability_repo.get_voice_language_capability(voice.id, target_lang)
        return bool(m2m_cap and m2m_cap.supported and m2m_cap.enabled)

    def get_compatible_voices(self, language_code: str) -> List[Voice]:
        """Returns all active voices compatible with the specified language."""
        return self.voice_repo.list_voices(language_code=language_code, active_only=True)

    # -------------------------------------------------------------------------
    # Authoritative Level 3 TTS Capability Validation
    # -------------------------------------------------------------------------

    def validate_tts_capability(
        self,
        voice_id: str,
        language_code: str,
        provider: Optional[str] = None,
    ) -> Tuple[Voice, Language]:
        """
        Authoritative validation pipeline for TTS synthesis requests (Level 3).
        Enforces:
        1. Language validity and active state (raises InvalidLanguageException)
        2. Voice validity and active state (raises InvalidVoiceException)
        3. Voice-Language compatibility (raises VoiceLanguageMismatchException)
        4. Provider language capability (raises InvalidLanguageException if provider disabled)

        Guarantees that external synthesis providers are never invoked on invalid requests.
        """
        clean_lang = (language_code or "").strip()
        clean_voice = (voice_id or "").strip()

        # 1. Validate Language
        if not clean_lang:
            raise InvalidLanguageException(
                message="The selected language is not available",
                language_code="",
            )

        lang = self.lang_repo.get_by_code(clean_lang)
        if not lang or not lang.is_active:
            raise InvalidLanguageException(
                message="The selected language is not available",
                language_code=clean_lang,
            )

        # 2. Validate Voice
        if not clean_voice:
            raise InvalidVoiceException(
                message="The selected voice is not available",
                voice_id="",
            )

        voice = self.voice_repo.get_by_voice_id(clean_voice)
        if not voice or not voice.is_active:
            raise InvalidVoiceException(
                message="The selected voice is not available",
                voice_id=clean_voice,
            )

        # 3. Validate Compatibility
        supported_langs = self.get_supported_languages_for_voice(voice)
        if clean_lang not in supported_langs:
            raise VoiceLanguageMismatchException(
                message=f"Voice '{clean_voice}' does not support language '{clean_lang}'",
                voice_id=clean_voice,
                language_code=clean_lang,
            )

        # 4. Validate Provider Capability (if explicit provider check requested)
        if provider:
            cap = self.capability_repo.get_provider_capability(provider, clean_lang)
            if cap and (not cap.supported or not cap.enabled):
                raise InvalidLanguageException(
                    message=f"Language '{clean_lang}' is not available for provider '{provider}'",
                    language_code=clean_lang,
                )

        return voice, lang
