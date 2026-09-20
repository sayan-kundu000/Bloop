"""
Unit tests for Bloop LanguageService and LanguageRepository.
Verifies language listing, metadata retrieval, direction handling, and provider mapping.
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.models.language import Language
from backend.app.services.language_service import LanguageService
from backend.app.repositories.capability_repository import CapabilityRepository


class TestLanguageService:
    """Unit tests for LanguageService business logic."""

    def test_list_languages_active_only(self, db_session: Session):
        service = LanguageService(db_session)
        languages = service.get_languages(active_only=True)
        assert len(languages) > 0
        for lang in languages:
            assert lang.is_active is True
            assert lang.code is not None
            assert lang.name is not None
            assert lang.direction in ("ltr", "rtl")

    def test_get_language_by_code(self, db_session: Session):
        service = LanguageService(db_session)
        en_lang = service.get_language("en-US")
        assert en_lang is not None
        assert en_lang.code == "en-US"
        assert en_lang.name == "English (US)"
        assert en_lang.direction == "ltr"

        non_existent = service.get_language("non-existent-code")
        assert non_existent is None

    def test_is_language_active(self, db_session: Session):
        service = LanguageService(db_session)
        assert service.is_language_active("en-US") is True
        assert service.is_language_active("unknown-locale") is False
        assert service.is_language_active("") is False

    def test_resolve_provider_language_default(self, db_session: Session):
        service = LanguageService(db_session)
        # Without custom mapping, returns original code
        resolved = service.resolve_provider_language("en-US", provider="elevenlabs")
        assert resolved == "en-US"

    def test_resolve_provider_language_with_custom_mapping(self, db_session: Session):
        service = LanguageService(db_session)
        cap_repo = CapabilityRepository(db_session)

        # Register custom mapping for Spanish: es-ES -> es
        cap_repo.set_provider_capability(
            provider="elevenlabs",
            language_code="es-ES",
            provider_language_code="es",
            supported=True,
            enabled=True,
        )

        resolved = service.resolve_provider_language("es-ES", provider="elevenlabs")
        assert resolved == "es"
