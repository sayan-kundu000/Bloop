"""
Bloop Favorite Service Automated Tests
Validates bookmark creation, duplicate prevention, cross-user ownership isolation,
removal, generation-based removal, and paginated search (Prompt 16 §61-66).
"""

import uuid
import pytest
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.favorite import Favorite
from backend.app.services.favorites.service import FavoriteService
from backend.app.core.exceptions import (
    ResourceNotFoundException,
    AuthorizationException,
    ConflictException,
)


@pytest.fixture
def favorite_test_fixture(db_session: Session):
    """Sets up primary user, secondary user, and generations for favorite testing."""
    user = User(
        email=f"fav_user_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass",
        full_name="Favorite User",
        is_active=True,
    )
    other_user = User(
        email=f"fav_other_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass",
        full_name="Other User",
        is_active=True,
    )
    db_session.add(user)
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(other_user)

    # User generations
    gen_1 = SpeechGeneration(
        user_id=user.id,
        text="Quantum entanglement in synthesized speech",
        char_count=42,
        word_count=5,
        language_code="en-US",
        voice_id="v-alpha",
        voice_name="Voice Alpha",
        audio_filename=f"fav-test-1-{uuid.uuid4().hex}.mp3",
        duration_seconds=2.4,
        file_size_bytes=1024,
    )
    gen_2 = SpeechGeneration(
        user_id=user.id,
        text="Acoustic harmonics resonance audio",
        char_count=35,
        word_count=4,
        language_code="en-GB",
        voice_id="v-beta",
        voice_name="Voice Beta",
        audio_filename=f"fav-test-2-{uuid.uuid4().hex}.mp3",
        duration_seconds=3.1,
        file_size_bytes=2048,
    )
    # Other user generation
    gen_other = SpeechGeneration(
        user_id=other_user.id,
        text="Private foreign speech generation",
        char_count=33,
        word_count=4,
        language_code="es-ES",
        voice_id="v-gamma",
        voice_name="Voice Gamma",
        audio_filename=f"fav-other-{uuid.uuid4().hex}.mp3",
        duration_seconds=1.9,
        file_size_bytes=512,
    )

    db_session.add_all([gen_1, gen_2, gen_other])
    db_session.commit()
    db_session.refresh(gen_1)
    db_session.refresh(gen_2)
    db_session.refresh(gen_other)

    return {
        "user": user,
        "other_user": other_user,
        "gen_1": gen_1,
        "gen_2": gen_2,
        "gen_other": gen_other,
    }


class TestFavoriteService:
    """Tests for the FavoriteService domain operations."""

    def test_add_favorite_success(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        gen = favorite_test_fixture["gen_1"]

        res = service.add_favorite(user_id=user.id, generation_id=gen.id, label="Key Audio")
        assert res.id is not None
        assert res.user_id == user.id
        assert res.generation_id == gen.id
        assert res.label == "Key Audio"
        assert res.generation is not None
        assert res.generation.is_favorite is True
        assert res.generation.id == gen.id

    def test_add_favorite_nonexistent_generation_raises_404(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]

        with pytest.raises(ResourceNotFoundException) as exc_info:
            service.add_favorite(user_id=user.id, generation_id=999999)
        assert exc_info.value.status_code == 404

    def test_add_favorite_cross_user_denied_raises_403(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        gen_other = favorite_test_fixture["gen_other"]

        # User A attempts to favorite User B's generation -> 403 Forbidden
        with pytest.raises(AuthorizationException) as exc_info:
            service.add_favorite(user_id=user.id, generation_id=gen_other.id)
        assert exc_info.value.status_code == 403

    def test_add_favorite_duplicate_raises_409_conflict(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        gen = favorite_test_fixture["gen_1"]

        service.add_favorite(user_id=user.id, generation_id=gen.id)

        # Re-favoriting the same generation raises 409 Conflict
        with pytest.raises(ConflictException) as exc_info:
            service.add_favorite(user_id=user.id, generation_id=gen.id)
        assert exc_info.value.status_code == 409

    def test_remove_favorite_success(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        gen = favorite_test_fixture["gen_1"]

        fav = service.add_favorite(user_id=user.id, generation_id=gen.id)
        fav_id = fav.id

        deleted_id = service.remove_favorite(favorite_id=fav_id, user=user)
        assert deleted_id == fav_id

        # Verification: underlying generation remains completely intact
        refreshed_gen = db_session.get(SpeechGeneration, gen.id)
        assert refreshed_gen is not None

    def test_remove_favorite_cross_user_denied_raises_403(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        other_user = favorite_test_fixture["other_user"]
        gen_other = favorite_test_fixture["gen_other"]

        # Other user favorites their own generation
        fav = service.add_favorite(user_id=other_user.id, generation_id=gen_other.id)

        # Primary user attempts to delete other user's favorite
        with pytest.raises(AuthorizationException) as exc_info:
            service.remove_favorite(favorite_id=fav.id, user=user)
        assert exc_info.value.status_code == 403

    def test_remove_favorite_by_generation_success(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        gen = favorite_test_fixture["gen_2"]

        service.add_favorite(user_id=user.id, generation_id=gen.id)

        # Remove via generation ID
        deleted_id = service.remove_favorite_by_generation(user_id=user.id, generation_id=gen.id)
        assert deleted_id is not None

        # Verify favorite is gone
        fav_check = db_session.query(Favorite).filter_by(user_id=user.id, generation_id=gen.id).first()
        assert fav_check is None

    def test_list_favorites_pagination_and_search(self, db_session: Session, favorite_test_fixture):
        service = FavoriteService(db_session)
        user = favorite_test_fixture["user"]
        gen_1 = favorite_test_fixture["gen_1"]
        gen_2 = favorite_test_fixture["gen_2"]

        service.add_favorite(user_id=user.id, generation_id=gen_1.id, label="Quantum tag")
        service.add_favorite(user_id=user.id, generation_id=gen_2.id, label="Acoustics tag")

        # List all
        items, total = service.list_favorites(user_id=user.id, page=1, page_size=10)
        assert total == 2
        assert len(items) == 2

        # Search by generation text
        search_items, search_total = service.list_favorites(user_id=user.id, search="Quantum")
        assert search_total == 1
        assert search_items[0].generation.id == gen_1.id

        # Search by voice name
        voice_items, voice_total = service.list_favorites(user_id=user.id, search="Beta")
        assert voice_total == 1
        assert voice_items[0].generation.id == gen_2.id

        # Filter by language
        lang_items, lang_total = service.list_favorites(user_id=user.id, language="en-GB")
        assert lang_total == 1
        assert lang_items[0].generation.language_code == "en-GB"
