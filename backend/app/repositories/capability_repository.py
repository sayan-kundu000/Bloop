"""
Bloop Capability Repository (SQLAlchemy 2.x)
Manages provider capabilities and voice-language compatibility relationships.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.capability import ProviderCapability, VoiceLanguageCapability


class CapabilityRepository:
    """Repository handling ProviderCapability and VoiceLanguageCapability queries."""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # Provider Capability Operations
    # -------------------------------------------------------------------------

    def get_provider_capability(
        self, provider: str, language_code: str
    ) -> Optional[ProviderCapability]:
        """Fetch provider capability entry for a specific language."""
        stmt = (
            select(ProviderCapability)
            .where(
                ProviderCapability.provider == provider,
                ProviderCapability.language_code == language_code,
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_provider_capabilities(
        self, provider: Optional[str] = None, enabled_only: bool = True
    ) -> List[ProviderCapability]:
        """List provider capabilities, optionally filtered by provider and enabled state."""
        stmt = select(ProviderCapability)
        if provider:
            stmt = stmt.where(ProviderCapability.provider == provider)
        if enabled_only:
            stmt = stmt.where(
                ProviderCapability.supported.is_(True),
                ProviderCapability.enabled.is_(True),
            )
        return list(self.db.execute(stmt).scalars().all())

    def set_provider_capability(
        self,
        provider: str,
        language_code: str,
        provider_language_code: Optional[str] = None,
        supported: bool = True,
        enabled: bool = True,
        metadata: Optional[dict] = None,
    ) -> ProviderCapability:
        """Create or update provider capability for a language."""
        existing = self.get_provider_capability(provider, language_code)
        if existing:
            existing.provider_language_code = provider_language_code
            existing.supported = supported
            existing.enabled = enabled
            if metadata is not None:
                existing.metadata_json = metadata
            self.db.commit()
            self.db.refresh(existing)
            return existing

        cap = ProviderCapability(
            provider=provider,
            language_code=language_code,
            provider_language_code=provider_language_code,
            supported=supported,
            enabled=enabled,
            metadata_json=metadata,
        )
        self.db.add(cap)
        self.db.commit()
        self.db.refresh(cap)
        return cap

    # -------------------------------------------------------------------------
    # Voice-Language Capability Operations
    # -------------------------------------------------------------------------

    def get_voice_language_capability(
        self, voice_id: int, language_code: str
    ) -> Optional[VoiceLanguageCapability]:
        """Check direct capability link between a voice and a language."""
        stmt = (
            select(VoiceLanguageCapability)
            .where(
                VoiceLanguageCapability.voice_id == voice_id,
                VoiceLanguageCapability.language_code == language_code,
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_voice_language_capabilities(
        self, voice_id: int, enabled_only: bool = True
    ) -> List[VoiceLanguageCapability]:
        """List all language capability mappings for a given voice ID."""
        stmt = select(VoiceLanguageCapability).where(VoiceLanguageCapability.voice_id == voice_id)
        if enabled_only:
            stmt = stmt.where(
                VoiceLanguageCapability.supported.is_(True),
                VoiceLanguageCapability.enabled.is_(True),
            )
        return list(self.db.execute(stmt).scalars().all())

    def link_voice_language(
        self,
        voice_id: int,
        language_code: str,
        supported: bool = True,
        enabled: bool = True,
        metadata: Optional[dict] = None,
    ) -> VoiceLanguageCapability:
        """Create or update a voice-to-language capability mapping."""
        existing = self.get_voice_language_capability(voice_id, language_code)
        if existing:
            existing.supported = supported
            existing.enabled = enabled
            if metadata is not None:
                existing.metadata_json = metadata
            self.db.commit()
            self.db.refresh(existing)
            return existing

        vlc = VoiceLanguageCapability(
            voice_id=voice_id,
            language_code=language_code,
            supported=supported,
            enabled=enabled,
            metadata_json=metadata,
        )
        self.db.add(vlc)
        self.db.commit()
        self.db.refresh(vlc)
        return vlc
