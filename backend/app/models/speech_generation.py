"""
Bloop Speech Generation Domain Model (SQLAlchemy 2.x)
Represents text-to-speech synthesis requests, lifecycle status, audio metadata,
and external provider tracking without storing large audio binary blobs.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.favorite import Favorite


class SpeechGeneration(Base):
    __tablename__ = "speech_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    voice_id: Mapped[str] = mapped_column(String(100), nullable=False)
    voice_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False, index=True)
    audio_filename: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    audio_format: Mapped[str] = mapped_column(String(10), default="mp3", nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="elevenlabs", nullable=False)
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="generations")
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="generation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_speech_generations_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<SpeechGeneration(id={self.id}, user_id={self.user_id}, "
            f"voice_id={self.voice_id!r}, status={self.status!r})>"
        )
