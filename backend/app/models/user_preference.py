"""
Bloop User Preference Domain Model (SQLAlchemy 2.x)
Represents user-specific UI settings, default speech parameters, and theme preferences.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.user import User


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    default_language_code: Mapped[Optional[str]] = mapped_column(
        ForeignKey("languages.code", ondelete="SET NULL"),
        nullable=True,
    )
    default_voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    theme: Mapped[str] = mapped_column(String(20), default="dark", nullable=False)
    audio_speed: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    auto_play: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preference")

    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, theme={self.theme!r}, speed={self.audio_speed})>"
