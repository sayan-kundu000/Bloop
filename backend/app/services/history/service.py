"""
Bloop Speech History Domain Service
Encapsulates business logic for speech generation history, pagination, search,
controlled sorting, resource ownership verification, and physical audio asset deletion.
"""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AuthorizationException,
    ResourceNotFoundException,
    ValidationException,
)
from backend.app.models.user import User
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.repositories.speech_generation import SpeechGenerationRepository
from backend.app.repositories.favorite import FavoriteRepository
from backend.app.services.audio.delivery import AudioDeliveryService
from backend.app.schemas.history import HistoryItemResponse, HistoryQueryFilter


class HistoryService:
    """Service managing speech generation history querying, detail inspection, and secure deletion."""

    def __init__(self, db: Session):
        self.db = db
        self.gen_repo = SpeechGenerationRepository(db)
        self.fav_repo = FavoriteRepository(db)
        self.audio_delivery = AudioDeliveryService()

    def _map_to_response(self, item: SpeechGeneration, fav_id: Optional[int] = None) -> HistoryItemResponse:
        """Enrich a SpeechGeneration model with dynamic URLs and user bookmark status."""
        is_fav = fav_id is not None
        audio_url = f"{settings.API_V1_PREFIX}/tts/audio/{item.audio_filename}"
        download_url = f"{settings.API_V1_PREFIX}/tts/download/{item.audio_filename}"

        return HistoryItemResponse(
            id=item.id,
            user_id=item.user_id,
            text=item.text,
            char_count=item.char_count,
            word_count=item.word_count,
            language_code=item.language_code,
            voice_id=item.voice_id,
            voice_name=item.voice_name,
            status=item.status,
            audio_url=audio_url,
            download_url=download_url,
            duration_seconds=item.duration_seconds or 0.0,
            file_size_bytes=item.file_size_bytes or 0,
            provider=item.provider,
            is_favorite=is_fav,
            favorite_id=fav_id,
            created_at=item.created_at,
        )

    def list_history(
        self,
        user_id: int,
        filter_params: HistoryQueryFilter,
    ) -> Tuple[List[HistoryItemResponse], int]:
        """
        List speech generation records strictly scoped to the requesting user's identity.
        Applies keyword search, language filtering, status filtering, favorite filtering,
        date range filtering, controlled sorting, and bounded pagination.
        Uses a joined query to eliminate N+1 queries for favorite state.
        """
        if filter_params.created_after and filter_params.created_before:
            if filter_params.created_after > filter_params.created_before:
                raise ValidationException("created_after cannot be later than created_before.")

        items, total = self.gen_repo.list_by_user(
            user_id=user_id,
            search=filter_params.search,
            language=filter_params.language,
            status=filter_params.status,
            favorite=filter_params.favorite,
            created_after=filter_params.created_after,
            created_before=filter_params.created_before,
            sort_by=filter_params.sort_by,
            order=filter_params.order,
            page=filter_params.page,
            page_size=filter_params.page_size,
        )

        response_items = [self._map_to_response(item, fav_id) for item, fav_id in items]
        return response_items, total

    def get_generation_detail(self, generation_id: int, user: User) -> HistoryItemResponse:
        """
        Retrieve single speech generation detail with strict resource ownership enforcement.
        Raises ResourceNotFoundException if record does not exist.
        Raises AuthorizationException if record belongs to another user (Prompt 15 §19 & §25).
        """
        gen = self.gen_repo.get_by_id(generation_id)
        if not gen:
            raise ResourceNotFoundException(resource="SpeechGeneration", identifier=generation_id)

        if gen.user_id is not None and gen.user_id != user.id and not user.is_superuser:
            raise AuthorizationException("You do not have permission to view this speech generation.")

        fav = self.fav_repo.get_by_user_and_gen(user.id, gen.id)
        return self._map_to_response(gen, fav.id if fav else None)

    def delete_generation(self, generation_id: int, user: User) -> bool:
        """
        Delete a speech generation record and remove its corresponding temporary audio file.
        Enforces strict ownership verification prior to deletion.
        """
        gen = self.gen_repo.get_by_id(generation_id)
        if not gen:
            raise ResourceNotFoundException(resource="SpeechGeneration", identifier=generation_id)

        if gen.user_id is not None and gen.user_id != user.id and not user.is_superuser:
            raise AuthorizationException("You do not have permission to delete this generation record.")

        # Clean up temporary disk audio asset if present
        if gen.audio_filename:
            self.audio_delivery.delete_audio_file(gen.audio_filename)

        # Delete database record transactionally
        self.gen_repo.delete(gen)
        return True
