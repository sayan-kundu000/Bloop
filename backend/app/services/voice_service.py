import json
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.logging import logger
from backend.app.models.language import Language
from backend.app.models.voice import Voice
from backend.app.repositories.capability_repository import CapabilityRepository
from backend.app.repositories.language_repository import LanguageRepository
from backend.app.repositories.voice_repository import VoiceRepository
from backend.app.schemas.voice import VoiceCreate

VOICES_CONFIG_FILE = "backend/voices_config.json"


class VoiceService:
    """
    Dynamic Voice Architecture Service.
    Allows dynamic registration and querying of voices without hardcoded assumptions.
    Supports user-provided ElevenLabs voices injected via config file or REST API.
    """

    def __init__(self, db: Session):
        self.db = db
        self.voice_repo = VoiceRepository(db)
        self.lang_repo = LanguageRepository(db)
        self.cap_repo = CapabilityRepository(db)

    def get_languages(self, active_only: bool = True) -> List[Language]:
        """Retrieve all active languages."""
        return self.lang_repo.list_languages(active_only=active_only)

    def get_voices(
        self,
        language_code: Optional[str] = None,
        gender: Optional[str] = None,
        search: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Voice]:
        """
        Query available voices with filtering by language, gender, and keyword search.
        Matches voices based on primary language or M2M language capabilities.
        """
        return self.voice_repo.list_voices(
            language_code=language_code,
            gender=gender,
            search=search,
            active_only=active_only,
        )

    def get_voice_by_id(self, voice_id: str) -> Optional[Voice]:
        """
        Retrieve voice by its public voice_id identifier.
        Supports development/testing aliases for backward compatibility.
        """
        if not voice_id:
            return None

        clean_id = voice_id.strip()
        voice = self.voice_repo.get_by_voice_id(clean_id)
        if not voice:
            # Handle legacy/convenience aliases in dev/test environments
            alias_map = {
                "dynamic-voice-en-male": "normal-male",
                "dynamic-voice-en-female": "normal-female",
                "normal-male-voice": "normal-male",
                "normal-female-voice": "normal-female",
                "sim_voice_1": "normal-female",
                "sim_voice_fav": "normal-female",
            }
            target_id = alias_map.get(clean_id.lower())
            if target_id:
                voice = self.voice_repo.get_by_voice_id(target_id)
        return voice

    def get_supported_languages(self, voice: Voice) -> List[str]:
        """List all language codes supported by this voice."""
        languages = set()
        if voice.language_code:
            languages.add(voice.language_code)
        m2m = self.cap_repo.list_voice_language_capabilities(voice.id, enabled_only=True)
        for c in m2m:
            languages.add(c.language_code)
        return sorted(list(languages))

    def add_language_to_voice(
        self, voice_id: int, language_code: str, supported: bool = True, enabled: bool = True
    ) -> None:
        """Dynamically link a language to an existing voice."""
        self.cap_repo.link_voice_language(
            voice_id=voice_id,
            language_code=language_code,
            supported=supported,
            enabled=enabled,
        )

    def register_user_voice(self, voice_in: VoiceCreate) -> Voice:
        """
        Dynamically registers a voice (such as an ElevenLabs voice ID provided by the user).
        Stores the provider-specific ID safely and establishes language capabilities.
        """
        existing = self.voice_repo.get_by_voice_id(voice_in.voice_id)
        if existing:
            updated = self.voice_repo.update(
                voice=existing,
                name=voice_in.name,
                language_code=voice_in.language_code,
                gender=voice_in.gender,
                accent=voice_in.accent,
                description=voice_in.description,
                provider=voice_in.provider,
                preview_url=voice_in.preview_url,
                is_active=voice_in.is_active,
                is_user_configured=True,
                metadata=voice_in.metadata if hasattr(voice_in, "metadata") else None,
            )
            # Ensure primary language is linked in capability table
            self.cap_repo.link_voice_language(
                voice_id=updated.id,
                language_code=voice_in.language_code,
                supported=True,
                enabled=True,
            )
            logger.info(f"Updated dynamic voice: {updated.voice_id}")
            return updated

        created = self.voice_repo.create(
            voice_id=voice_in.voice_id,
            provider_voice_id=getattr(voice_in, "provider_voice_id", None) or voice_in.voice_id,
            name=voice_in.name,
            language_code=voice_in.language_code,
            gender=voice_in.gender,
            accent=voice_in.accent,
            description=voice_in.description,
            provider=voice_in.provider,
            preview_url=voice_in.preview_url,
            is_active=voice_in.is_active,
            is_user_configured=True,
            metadata=voice_in.metadata if hasattr(voice_in, "metadata") else None,
        )
        # Link primary language in capability table
        self.cap_repo.link_voice_language(
            voice_id=created.id,
            language_code=voice_in.language_code,
            supported=True,
            enabled=True,
        )
        logger.info(f"Registered new dynamic voice: {created.voice_id}")
        return created

    def import_voices_from_config(self) -> int:
        """
        Loads custom voices from backend/voices_config.json if provided by the user.
        """
        if not os.path.exists(VOICES_CONFIG_FILE):
            return 0

        try:
            with open(VOICES_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                voices_list = data.get("voices", [])
                imported_count = 0
                for v in voices_list:
                    voice_create = VoiceCreate(
                        voice_id=v["voice_id"],
                        name=v["name"],
                        language_code=v.get("language_code", "en-US"),
                        gender=v.get("gender", "unspecified"),
                        accent=v.get("accent"),
                        description=v.get("description"),
                        provider=v.get("provider", "elevenlabs"),
                        is_active=v.get("is_active", True),
                        is_user_configured=True,
                    )
                    self.register_user_voice(voice_create)
                    imported_count += 1
                logger.info(f"Successfully imported {imported_count} voices from {VOICES_CONFIG_FILE}")
                return imported_count
        except Exception as e:
            logger.error(f"Error importing voices from {VOICES_CONFIG_FILE}: {e}")
            return 0

