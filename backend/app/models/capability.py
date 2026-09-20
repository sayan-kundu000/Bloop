"""
Bloop TTS Provider and Voice Language Capability Models (SQLAlchemy 2.x)
Represents provider capabilities and many-to-many voice-language relationships.
Enables decoupling of external vendor constraints from internal catalog models.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.language import Language
    from backend.app.models.voice import Voice


class ProviderCapability(Base):
    """
    Represents whether an external TTS provider supports a specific language,
    and whether Bloop currently enables it for user traffic.
    """
    __tablename__ = "provider_capabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_language_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    supported: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    __table_args__ = (
        UniqueConstraint("provider", "language_code", name="uq_provider_language"),
    )

    # Relationships
    language: Mapped["Language"] = relationship("Language", back_populates="provider_capabilities")

    def __repr__(self) -> str:
        return f"<ProviderCapability(provider={self.provider!r}, lang={self.language_code!r}, enabled={self.enabled})>"


class VoiceLanguageCapability(Base):
    """
    Many-to-many relationship mapping voices to their supported languages.
    A single voice can support multiple locales/languages dynamically.
    """
    __tablename__ = "voice_language_capabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    voice_id: Mapped[int] = mapped_column(
        ForeignKey("voices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    supported: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("voice_id", "language_code", name="uq_voice_language"),
    )

    # Relationships
    voice: Mapped["Voice"] = relationship("Voice", back_populates="language_capabilities")
    language: Mapped["Language"] = relationship("Language", back_populates="voice_capabilities")

    def __repr__(self) -> str:
        return f"<VoiceLanguageCapability(voice_id={self.voice_id}, lang={self.language_code!r}, enabled={self.enabled})>"
