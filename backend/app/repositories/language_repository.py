"""
Bloop Language Catalog Repository (SQLAlchemy 2.x)
Handles persistence, lookup, and availability queries for languages.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.language import Language


class LanguageRepository:
    """Repository managing Language catalog queries and persistence."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Optional[Language]:
        """Fetch language by ISO/BCP-47 code (case-insensitive search)."""
        stmt = select(Language).where(Language.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_languages(self, active_only: bool = True) -> List[Language]:
        """List all registered languages, optionally filtered by is_active."""
        stmt = select(Language)
        if active_only:
            stmt = stmt.where(Language.is_active.is_(True))
        stmt = stmt.order_by(Language.name.asc())
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        code: str,
        name: str,
        native_name: Optional[str] = None,
        direction: str = "ltr",
        is_active: bool = True,
        metadata: Optional[dict] = None,
    ) -> Language:
        """Create and persist a new language record."""
        lang = Language(
            code=code,
            name=name,
            native_name=native_name,
            direction=direction,
            is_active=is_active,
            metadata_json=metadata,
        )
        self.db.add(lang)
        self.db.commit()
        self.db.refresh(lang)
        return lang

    def update(
        self,
        code: str,
        name: Optional[str] = None,
        native_name: Optional[str] = None,
        direction: Optional[str] = None,
        is_active: Optional[bool] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[Language]:
        """Update existing language attributes."""
        lang = self.get_by_code(code)
        if not lang:
            return None
        if name is not None:
            lang.name = name
        if native_name is not None:
            lang.native_name = native_name
        if direction is not None:
            lang.direction = direction
        if is_active is not None:
            lang.is_active = is_active
        if metadata is not None:
            lang.metadata_json = metadata
        self.db.commit()
        self.db.refresh(lang)
        return lang
