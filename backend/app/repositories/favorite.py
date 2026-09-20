"""
Bloop Favorite Repository (SQLAlchemy 2.x)
Encapsulates data persistence, uniqueness enforcement, and queries for Bookmarked Favorites.
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc, or_
from sqlalchemy.orm import Session, joinedload
from backend.app.models.favorite import Favorite
from backend.app.models.speech_generation import SpeechGeneration


class FavoriteRepository:
    """Repository handling persistence and queries for the Favorite domain."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, favorite_id: int) -> Optional[Favorite]:
        stmt = (
            select(Favorite)
            .options(joinedload(Favorite.generation))
            .where(Favorite.id == favorite_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_user_and_gen(self, user_id: int, gen_id: int) -> Optional[Favorite]:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.generation_id == gen_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user_id: int, gen_id: int, label: Optional[str] = None) -> Favorite:
        fav = Favorite(user_id=user_id, generation_id=gen_id, label=label)
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def list_by_user(
        self,
        user_id: int,
        search: Optional[str] = None,
        language: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Favorite], int]:
        """
        List favorites for a user with optional text search and language filtering.
        Eagerly loads the SpeechGeneration entity to eliminate N+1 queries.
        """
        stmt = (
            select(Favorite)
            .options(joinedload(Favorite.generation))
            .join(SpeechGeneration, Favorite.generation_id == SpeechGeneration.id)
            .where(Favorite.user_id == user_id)
        )
        count_stmt = (
            select(func.count(Favorite.id))
            .join(SpeechGeneration, Favorite.generation_id == SpeechGeneration.id)
            .where(Favorite.user_id == user_id)
        )

        if search and search.strip():
            clean_search = search.strip()
            search_filter = or_(
                SpeechGeneration.text.ilike(f"%{clean_search}%"),
                SpeechGeneration.voice_name.ilike(f"%{clean_search}%"),
                Favorite.label.ilike(f"%{clean_search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if language and language.strip():
            clean_lang = language.strip()
            stmt = stmt.where(SpeechGeneration.language_code == clean_lang)
            count_stmt = count_stmt.where(SpeechGeneration.language_code == clean_lang)

        total = self.db.execute(count_stmt).scalar_one()

        safe_page = max(1, page)
        safe_page_size = max(1, min(page_size, 100))

        stmt = (
            stmt.order_by(desc(Favorite.created_at), desc(Favorite.id))
            .offset((safe_page - 1) * safe_page_size)
            .limit(safe_page_size)
        )
        items = self.db.execute(stmt).scalars().all()
        return list(items), total

    def delete(self, fav: Favorite) -> None:
        self.db.delete(fav)
        self.db.commit()

    def delete_by_user_and_gen(self, user_id: int, gen_id: int) -> bool:
        fav = self.get_by_user_and_gen(user_id, gen_id)
        if fav:
            self.delete(fav)
            return True
        return False
