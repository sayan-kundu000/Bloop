"""
Bloop Language Domain Service
Encapsulates language catalog queries, activation checks, and provider mapping.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.language import Language
from backend.app.repositories.language_repository import LanguageRepository
from backend.app.repositories.capability_repository import CapabilityRepository


class LanguageService:
    """Service orchestrating language operations and provider language mappings."""

    def __init__(self, db: Session):
        self.db = db
        self.lang_repo = LanguageRepository(db)
        self.capability_repo = CapabilityRepository(db)

    def get_languages(self, active_only: bool = True) -> List[Language]:
        """Retrieve all registered languages."""
        return self.lang_repo.list_languages(active_only=active_only)

    def get_language(self, code: str) -> Optional[Language]:
        """Lookup language by code."""
        if not code or not code.strip():
            return None
        return self.lang_repo.get_by_code(code.strip())

    def is_language_active(self, code: str) -> bool:
        """Check if a language exists and is active in Bloop."""
        lang = self.get_language(code)
        return bool(lang and lang.is_active)

    def resolve_provider_language(self, code: str, provider: str = "elevenlabs") -> str:
        """
        Translates a Bloop language code to a provider-specific code if a custom mapping exists.
        Defaults to the Bloop language code if no explicit mapping is defined.
        """
        if not code:
            return "en-US"
        target_code = code.strip()
        cap = self.capability_repo.get_provider_capability(provider, target_code)
        if cap and cap.provider_language_code:
            return cap.provider_language_code
        return target_code
