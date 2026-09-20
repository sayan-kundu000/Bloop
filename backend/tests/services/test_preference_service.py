"""
Bloop Preference Service Automated Tests
Validates preference retrieval, default initialization, bounds checking,
and theme/speed/language validation (Prompt 15 §9-12).
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.language import Language
from backend.app.services.preferences.service import PreferenceService
from backend.app.schemas.user import UserPreferenceUpdate
from backend.app.core.exceptions import ValidationException


@pytest.fixture
def pref_user(db_session: Session) -> User:
    """Creates a user for testing preference services."""
    import uuid
    user = User(
        email=f"pref_test_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_test_pass",
        full_name="Pref User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Ensure en-US language exists
    lang = db_session.query(Language).filter(Language.code == "en-US").first()
    if not lang:
        lang = Language(code="en-US", name="English", is_active=True)
        db_session.add(lang)
        db_session.commit()

    return user


class TestPreferenceService:
    """Tests for PreferenceService domain logic and validation rules."""

    def test_get_preferences_initializes_defaults(
        self, db_session: Session, pref_user: User
    ):
        service = PreferenceService(db_session)
        prefs = service.get_preferences(pref_user.id)

        assert prefs.user_id == pref_user.id
        assert prefs.theme == "dark"
        assert prefs.audio_speed == 1.0
        assert prefs.auto_play is True
        assert prefs.default_language_code is None
        assert prefs.default_voice_id is None

    def test_update_preferences_valid_theme_and_speed(
        self, db_session: Session, pref_user: User
    ):
        service = PreferenceService(db_session)
        req = UserPreferenceUpdate(theme="light", audio_speed=1.5, auto_play=False)
        updated = service.update_preferences(pref_user.id, req)

        assert updated.theme == "light"
        assert updated.audio_speed == 1.5
        assert updated.auto_play is False

    def test_update_preferences_invalid_theme_rejected(
        self, db_session: Session, pref_user: User
    ):
        service = PreferenceService(db_session)
        req = UserPreferenceUpdate.model_construct(theme="neon-rainbow")
        with pytest.raises(ValidationException) as exc_info:
            service.update_preferences(pref_user.id, req)
        assert "Theme must be one of" in str(exc_info.value.message)

    def test_update_preferences_speed_out_of_bounds_rejected(
        self, db_session: Session, pref_user: User
    ):
        service = PreferenceService(db_session)
        # Below 0.5
        req_low = UserPreferenceUpdate.model_construct(audio_speed=0.2)
        with pytest.raises(ValidationException) as exc_low:
            service.update_preferences(pref_user.id, req_low)
        assert "must be between 0.5 and 2.0" in str(exc_low.value.message)

        # Above 2.0
        req_high = UserPreferenceUpdate.model_construct(audio_speed=3.5)
        with pytest.raises(ValidationException) as exc_high:
            service.update_preferences(pref_user.id, req_high)
        assert "must be between 0.5 and 2.0" in str(exc_high.value.message)

    def test_update_preferences_valid_and_invalid_language(
        self, db_session: Session, pref_user: User
    ):
        service = PreferenceService(db_session)

        # Valid language en-US
        req_valid = UserPreferenceUpdate(default_language_code="en-US")
        updated = service.update_preferences(pref_user.id, req_valid)
        assert updated.default_language_code == "en-US"

        # Invalid unregistered language
        req_invalid = UserPreferenceUpdate(default_language_code="xx-ZZ")
        with pytest.raises(ValidationException) as exc_info:
            service.update_preferences(pref_user.id, req_invalid)
        assert "not registered or supported" in str(exc_info.value.message)

    def test_update_preferences_clear_defaults(
        self, db_session: Session, pref_user: User
    ):
        service = PreferenceService(db_session)

        # Set values
        service.update_preferences(
            pref_user.id,
            UserPreferenceUpdate(default_language_code="en-US", default_voice_id="custom-v1")
        )

        # Clear them by passing empty strings
        cleared = service.update_preferences(
            pref_user.id,
            UserPreferenceUpdate(default_language_code="", default_voice_id="")
        )
        assert cleared.default_language_code is None
        assert cleared.default_voice_id is None
