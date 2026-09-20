"""
Bloop Speech Generation Repository (SQLAlchemy 2.x)
Encapsulates data persistence, ownership queries, and pagination for Speech Generations.
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc, Integer
from sqlalchemy.orm import Session
from backend.app.models.speech_generation import SpeechGeneration


class SpeechGenerationRepository:
    """Repository handling persistence and queries for the Speech Generation domain."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, gen_id: int) -> Optional[SpeechGeneration]:
        stmt = select(SpeechGeneration).where(SpeechGeneration.id == gen_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_filename(self, filename: str) -> Optional[SpeechGeneration]:
        stmt = select(SpeechGeneration).where(SpeechGeneration.audio_filename == filename)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        text: str,
        char_count: int,
        word_count: int,
        language_code: str,
        voice_id: str,
        audio_filename: str,
        duration_seconds: float,
        file_size_bytes: int,
        provider: str,
        user_id: Optional[int] = None,
        voice_name: Optional[str] = None,
        status: str = "completed",
        audio_format: str = "mp3",
        provider_request_id: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> SpeechGeneration:
        gen = SpeechGeneration(
            user_id=user_id,
            text=text,
            char_count=char_count,
            word_count=word_count,
            language_code=language_code,
            voice_id=voice_id,
            voice_name=voice_name,
            status=status,
            audio_filename=audio_filename,
            duration_seconds=duration_seconds,
            file_size_bytes=file_size_bytes,
            audio_format=audio_format,
            provider=provider,
            provider_request_id=provider_request_id,
            error_code=error_code,
            error_message=error_message,
        )
        self.db.add(gen)
        self.db.commit()
        self.db.refresh(gen)
        return gen

    def update_status(
        self,
        gen_id: int,
        status: str,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[SpeechGeneration]:
        gen = self.get_by_id(gen_id)
        if gen:
            gen.status = status
            if error_code is not None:
                gen.error_code = error_code
            if error_message is not None:
                gen.error_message = error_message
            self.db.commit()
            self.db.refresh(gen)
        return gen

    def record_failure(
        self,
        text: str,
        char_count: int,
        word_count: int,
        language_code: str,
        voice_id: str,
        provider: str,
        error_code: str,
        error_message: str,
        user_id: Optional[int] = None,
        voice_name: Optional[str] = None,
    ) -> SpeechGeneration:
        import uuid
        placeholder_filename = f"failed-{uuid.uuid4().hex}.mp3"
        return self.create(
            text=text,
            char_count=char_count,
            word_count=word_count,
            language_code=language_code,
            voice_id=voice_id,
            audio_filename=placeholder_filename,
            duration_seconds=0.0,
            file_size_bytes=0,
            provider=provider,
            user_id=user_id,
            voice_name=voice_name,
            status="failed",
            error_code=error_code,
            error_message=error_message,
        )

    def get_by_id_and_user(self, gen_id: int, user_id: int) -> Optional[SpeechGeneration]:
        """Fetch a generation record strictly scoped to a specific owning user ID."""
        stmt = select(SpeechGeneration).where(
            SpeechGeneration.id == gen_id,
            SpeechGeneration.user_id == user_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_user(
        self,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        language: Optional[str] = None,
        status: Optional[str] = None,
        favorite: Optional[bool] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Tuple[SpeechGeneration, Optional[int]]], int]:
        """
        List speech generations for a user with search, filtering, controlled sorting, and pagination.
        Performs an outer join with Favorite to retrieve bookmark state in a single query (eliminates N+1).
        Enforces server-side pagination boundaries and strict column allowlisting.
        """
        from sqlalchemy import or_, asc, desc
        from backend.app.models.favorite import Favorite

        if user_id is not None:
            stmt = select(SpeechGeneration, Favorite.id.label("favorite_id")).outerjoin(
                Favorite,
                (Favorite.generation_id == SpeechGeneration.id) & (Favorite.user_id == user_id),
            ).where(SpeechGeneration.user_id == user_id)

            count_stmt = select(func.count(SpeechGeneration.id)).where(SpeechGeneration.user_id == user_id)
            if favorite is not None:
                count_stmt = count_stmt.select_from(SpeechGeneration).outerjoin(
                    Favorite,
                    (Favorite.generation_id == SpeechGeneration.id) & (Favorite.user_id == user_id),
                )
        else:
            stmt = select(SpeechGeneration, func.cast(None, Integer).label("favorite_id"))
            count_stmt = select(func.count(SpeechGeneration.id))

        if favorite is True:
            stmt = stmt.where(Favorite.id.is_not(None))
            count_stmt = count_stmt.where(Favorite.id.is_not(None))
        elif favorite is False:
            stmt = stmt.where(Favorite.id.is_(None))
            count_stmt = count_stmt.where(Favorite.id.is_(None))

        if search and search.strip():
            clean_search = search.strip()
            search_filter = or_(
                SpeechGeneration.text.ilike(f"%{clean_search}%"),
                SpeechGeneration.voice_name.ilike(f"%{clean_search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if language and language.strip():
            clean_lang = language.strip()
            stmt = stmt.where(SpeechGeneration.language_code == clean_lang)
            count_stmt = count_stmt.where(SpeechGeneration.language_code == clean_lang)

        if status and status.strip():
            clean_status = status.strip().lower()
            stmt = stmt.where(SpeechGeneration.status == clean_status)
            count_stmt = count_stmt.where(SpeechGeneration.status == clean_status)

        if created_after is not None:
            stmt = stmt.where(SpeechGeneration.created_at >= created_after)
            count_stmt = count_stmt.where(SpeechGeneration.created_at >= created_after)

        if created_before is not None:
            stmt = stmt.where(SpeechGeneration.created_at <= created_before)
            count_stmt = count_stmt.where(SpeechGeneration.created_at <= created_before)

        total = self.db.execute(count_stmt).scalar_one()

        # Controlled sort column allowlist (Prompt 15 §24, Prompt 16 §25)
        sort_column_map = {
            "created_at": SpeechGeneration.created_at,
            "duration_seconds": SpeechGeneration.duration_seconds,
            "char_count": SpeechGeneration.char_count,
            "word_count": SpeechGeneration.word_count,
        }
        target_column = sort_column_map.get(sort_by, SpeechGeneration.created_at)
        sort_expr = asc(target_column) if order.lower() == "asc" else desc(target_column)

        # Server-side bounded pagination limits
        safe_page = max(1, page)
        safe_page_size = max(1, min(page_size, 100))

        stmt = (
            stmt.order_by(sort_expr, desc(SpeechGeneration.id))
            .offset((safe_page - 1) * safe_page_size)
            .limit(safe_page_size)
        )
        rows = self.db.execute(stmt).all()
        items = [(row[0], row[1]) for row in rows]
        return items, total

    def delete(self, gen: SpeechGeneration) -> None:
        self.db.delete(gen)
        self.db.commit()

