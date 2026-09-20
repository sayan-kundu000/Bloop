"""
Bloop Favorites Domain Service
Encapsulates business logic for bookmarking, ownership validation, duplicate conflict prevention,
and retrieval of favorite speech generations without duplicating underlying speech entities.
"""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AuthorizationException,
    ConflictException,
    ResourceNotFoundException,
)
from backend.app.models.user import User
from backend.app.models.favorite import Favorite
from backend.app.repositories.favorite import FavoriteRepository
from backend.app.repositories.speech_generation import SpeechGenerationRepository
from backend.app.schemas.favorite import FavoriteResponse
from backend.app.schemas.history import HistoryItemResponse


class FavoriteService:
    """Service managing bookmarks and saved generations for authenticated users."""

    def __init__(self, db: Session):
        self.db = db
        self.fav_repo = FavoriteRepository(db)
        self.gen_repo = SpeechGenerationRepository(db)

    def _map_to_response(self, fav: Favorite) -> FavoriteResponse:
        """Enrich a Favorite model and its embedded SpeechGeneration with dynamic URLs."""
        gen_res = None
        if fav.generation:
            gen = fav.generation
            audio_url = f"{settings.API_V1_PREFIX}/tts/audio/{gen.audio_filename}"
            download_url = f"{settings.API_V1_PREFIX}/tts/download/{gen.audio_filename}"
            gen_res = HistoryItemResponse(
                id=gen.id,
                user_id=gen.user_id,
                text=gen.text,
                char_count=gen.char_count,
                word_count=gen.word_count,
                language_code=gen.language_code,
                voice_id=gen.voice_id,
                voice_name=gen.voice_name,
                status=gen.status.value if hasattr(gen.status, "value") else str(gen.status),
                audio_url=audio_url,
                download_url=download_url,
                duration_seconds=gen.duration_seconds or 0.0,
                file_size_bytes=gen.file_size_bytes or 0,
                provider=gen.provider or "elevenlabs",
                is_favorite=True,
                favorite_id=fav.id,
                created_at=gen.created_at,
            )

        return FavoriteResponse(
            id=fav.id,
            user_id=fav.user_id,
            generation_id=fav.generation_id,
            label=fav.label,
            created_at=fav.created_at,
            generation=gen_res,
        )

    def list_favorites(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Tuple[List[FavoriteResponse], int]:
        """
        Retrieve paginated favorite speech generations strictly scoped to the requesting user.
        Supports optional search and language filtering. Eagerly loads generation records (no N+1).
        """
        items, total = self.fav_repo.list_by_user(
            user_id=user_id,
            search=search,
            language=language,
            page=page,
            page_size=page_size,
        )
        return [self._map_to_response(item) for item in items], total

    def add_favorite(
        self,
        user_id: int,
        generation_id: int,
        label: Optional[str] = None,
    ) -> FavoriteResponse:
        """
        Bookmark a speech generation record.
        Enforces generation existence, strict user ownership, and duplicate conflict checks.
        """
        gen = self.gen_repo.get_by_id(generation_id)
        if not gen:
            raise ResourceNotFoundException(resource="SpeechGeneration", identifier=generation_id)

        # Prevent cross-user favorites (Prompt 14 §40, Prompt 16 §7 & §62)
        if gen.user_id is not None and gen.user_id != user_id:
            raise AuthorizationException("You do not have permission to favorite another user's speech generation.")

        # Duplicate conflict check (Prompt 16 §8)
        existing = self.fav_repo.get_by_user_and_gen(user_id, generation_id)
        if existing:
            raise ConflictException(
                "Speech generation record is already in your favorites.",
                details={"generation_id": generation_id},
            )

        fav = self.fav_repo.create(user_id=user_id, gen_id=generation_id, label=label)
        fav.generation = gen
        return self._map_to_response(fav)

    def remove_favorite(self, favorite_id: int, user: User) -> int:
        """
        Remove a favorite bookmark by favorite ID with resource ownership verification.
        Preserves the underlying SpeechGeneration record intact.
        """
        fav = self.fav_repo.get_by_id(favorite_id)
        if not fav:
            raise ResourceNotFoundException(resource="Favorite", identifier=favorite_id)

        if fav.user_id != user.id and not user.is_superuser:
            raise AuthorizationException("You do not have permission to remove this favorite.")

        self.fav_repo.delete(fav)
        return favorite_id

    def remove_favorite_by_generation(self, user_id: int, generation_id: int) -> int:
        """
        Remove a favorite bookmark by generation ID for convenience from history/workspace views.
        """
        fav = self.fav_repo.get_by_user_and_gen(user_id, generation_id)
        if not fav:
            raise ResourceNotFoundException(resource="Favorite", identifier=f"generation_{generation_id}")

        fav_id = fav.id
        self.fav_repo.delete(fav)
        return fav_id
