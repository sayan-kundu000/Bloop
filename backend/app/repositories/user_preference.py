"""
Bloop User Preference Repository (SQLAlchemy 2.x)
Encapsulates data persistence and queries for the UserPreference domain.
"""

from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.user_preference import UserPreference


class UserPreferenceRepository:
    """Repository handling persistence and queries for user UI and speech preferences."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[UserPreference]:
        """Fetch user preferences by owning user ID."""
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        user_id: int,
        theme: str = "dark",
        audio_speed: float = 1.0,
        auto_play: bool = True,
        default_language_code: Optional[str] = None,
        default_voice_id: Optional[str] = None,
    ) -> UserPreference:
        """Create a new user preference record."""
        pref = UserPreference(
            user_id=user_id,
            theme=theme,
            audio_speed=audio_speed,
            auto_play=auto_play,
            default_language_code=default_language_code,
            default_voice_id=default_voice_id,
        )
        self.db.add(pref)
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def get_or_create(self, user_id: int) -> UserPreference:
        """Retrieve existing preferences or initialize default preferences."""
        pref = self.get_by_user_id(user_id)
        if not pref:
            pref = self.create(user_id=user_id)
        return pref

    def update(self, pref: UserPreference, update_data: Dict[str, Any]) -> UserPreference:
        """Apply updates to an existing preference record."""
        allowed_fields = {
            "theme",
            "audio_speed",
            "auto_play",
            "default_language_code",
            "default_voice_id",
        }
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(pref, field, value)

        self.db.commit()
        self.db.refresh(pref)
        return pref
