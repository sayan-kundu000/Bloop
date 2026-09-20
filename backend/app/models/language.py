"""
Bloop Language Catalog Domain Model (SQLAlchemy 2.x)
Represents standard ISO language and locale metadata for speech synthesis.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.voice import Voice
    from backend.app.models.capability import ProviderCapability, VoiceLanguageCapability


class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(10), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    direction: Mapped[str] = mapped_column(String(5), default="ltr", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    voices: Mapped[List["Voice"]] = relationship("Voice", back_populates="language")
    provider_capabilities: Mapped[List["ProviderCapability"]] = relationship(
        "ProviderCapability", back_populates="language", cascade="all, delete-orphan"
    )
    voice_capabilities: Mapped[List["VoiceLanguageCapability"]] = relationship(
        "VoiceLanguageCapability", back_populates="language", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Language(code={self.code!r}, name={self.name!r}, direction={self.direction!r}, active={self.is_active})>"

