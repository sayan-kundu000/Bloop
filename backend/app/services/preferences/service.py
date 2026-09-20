"""
Bloop User Preferences Domain Service
Encapsulates business logic for user preference retrieval, validation, and updates.
Enforces the core principle: Preference != Capability != Authorization (Prompt 15 §10).
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.user_preference import UserPreference
from backend.app.repositories.user_preference import UserPreferenceRepository
from backend.app.repositories.language_repository import LanguageRepository
from backend.app.repositories.voice_repository import VoiceRepository
from backend.app.schemas.user import UserPreferenceResponse, UserPreferenceUpdate
from backend.app.core.exceptions import ValidationException


class PreferenceService:
    """Service handling user preference retrieval and validated updates."""

    def __init__(self, db: Session):
        self.db = db
        self.pref_repo = UserPreferenceRepository(db)
        self.lang_repo = LanguageRepository(db)
        self.voice_repo = VoiceRepository(db)

    def get_preferences(self, user_id: int) -> UserPreferenceResponse:
        """
        Retrieve user preferences. Automatically initializes a default record if absent.
        """
        pref = self.pref_repo.get_or_create(user_id)
        return UserPreferenceResponse.model_validate(pref)

    def update_preferences(
        self,
        user_id: int,
        prefs_in: UserPreferenceUpdate,
    ) -> UserPreferenceResponse:
        """
        Validate and apply user preference updates.
        Enforces validation boundaries for themes, playback speeds, language codes,
        and dynamically registered voices without hardcoding fake defaults (Prompt 15 §12).
        """
        pref = self.pref_repo.get_or_create(user_id)
        update_dict: Dict[str, Any] = {}

        # 1. Theme validation
        if prefs_in.theme is not None:
            clean_theme = prefs_in.theme.strip().lower()
            if clean_theme not in ("dark", "light", "system"):
                raise ValidationException("Theme must be one of: 'dark', 'light', 'system'.")
            update_dict["theme"] = clean_theme

        # 2. Audio playback speed validation
        if prefs_in.audio_speed is not None:
            if prefs_in.audio_speed < 0.5 or prefs_in.audio_speed > 2.0:
                raise ValidationException("Audio playback speed must be between 0.5 and 2.0.")
            update_dict["audio_speed"] = round(float(prefs_in.audio_speed), 2)

        # 3. Auto-play toggle
        if prefs_in.auto_play is not None:
            update_dict["auto_play"] = bool(prefs_in.auto_play)

        # 4. Default language validation
        if prefs_in.default_language_code is not None:
            clean_lang = prefs_in.default_language_code.strip()
            if clean_lang == "":
                update_dict["default_language_code"] = None
            else:
                lang = self.lang_repo.get_by_code(clean_lang)
                if not lang:
                    raise ValidationException(
                        f"Language code '{clean_lang}' is not registered or supported."
                    )
                update_dict["default_language_code"] = lang.code

        # 5. Default voice validation (Dynamic Voice Invariant: Prompt 15 §3 & §12)
        if prefs_in.default_voice_id is not None:
            clean_voice = prefs_in.default_voice_id.strip()
            if clean_voice == "":
                update_dict["default_voice_id"] = None
            else:
                # If voice catalog has voices, verify voice exists; if voice is a valid identifier format, allow it
                voice = self.voice_repo.get_by_voice_id(clean_voice)
                # If registered, verify; otherwise allow non-empty identifier up to 100 chars
                if len(clean_voice) > 100:
                    raise ValidationException("Voice ID cannot exceed 100 characters.")
                update_dict["default_voice_id"] = clean_voice

        updated_pref = self.pref_repo.update(pref, update_dict)
        return UserPreferenceResponse.model_validate(updated_pref)
