"""
Bloop Dynamic Voice Registry Model (SQLAlchemy 2.x)
Represents dynamically registered TTS voice metadata.
CRITICAL INVARIANT: Contains zero hardcoded voice records or fabricated IDs.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.language import Language
    from backend.app.models.capability import VoiceLanguageCapability


class Voice(Base):
    __tablename__ = "voices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    voice_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    provider_voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gender: Mapped[str] = mapped_column(String(20), default="unspecified", nullable=False)
    accent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), default="dynamic", nullable=False)
    preview_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_user_configured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
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
    language: Mapped["Language"] = relationship("Language", back_populates="voices")
    language_capabilities: Mapped[List["VoiceLanguageCapability"]] = relationship(
        "VoiceLanguageCapability", back_populates="voice", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Voice(id={self.id}, voice_id={self.voice_id!r}, name={self.name!r}, lang={self.language_code})>"

