"""
Bloop Favorite & Organization Security Isolation Tests
Verifies multi-tenant boundaries, anti-IDOR protections, cascade delete integrity,
and non-leakage of cross-user bookmark data (Prompt 16 §62, §66, §79).
"""

import uuid
import pytest
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.favorite import Favorite
from backend.app.services.favorites.service import FavoriteService
from backend.app.services.history.service import HistoryService
from backend.app.core.exceptions import AuthorizationException


@pytest.fixture
def multi_user_fixture(db_session: Session):
    """Creates two distinct isolated users with speech generations and favorites."""
    user_a = User(
        email=f"sec_a_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass_a",
        full_name="User Alpha",
        is_active=True,
    )
    user_b = User(
        email=f"sec_b_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass_b",
        full_name="User Beta",
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    gen_a = SpeechGeneration(
        user_id=user_a.id,
        text="Private speech content belonging to User A",
        char_count=43,
        word_count=7,
        language_code="en-US",
        voice_id="voice-a",
        voice_name="Voice A",
        audio_filename=f"sec-a-{uuid.uuid4().hex}.mp3",
        duration_seconds=2.0,
        file_size_bytes=1000,
    )
    gen_b = SpeechGeneration(
        user_id=user_b.id,
        text="Confidential speech output belonging to User B",
        char_count=46,
        word_count=7,
        language_code="en-US",
        voice_id="voice-b",
        voice_name="Voice B",
        audio_filename=f"sec-b-{uuid.uuid4().hex}.mp3",
        duration_seconds=2.5,
        file_size_bytes=1200,
    )
    db_session.add_all([gen_a, gen_b])
    db_session.commit()
    db_session.refresh(gen_a)
    db_session.refresh(gen_b)

    return {
        "user_a": user_a,
        "user_b": user_b,
        "gen_a": gen_a,
        "gen_b": gen_b,
    }


class TestFavoriteSecurityIsolation:
    """Security tests verifying cross-tenant defenses on favorites and organization."""

    def test_user_a_cannot_favorite_user_b_generation(self, db_session: Session, multi_user_fixture):
        fav_service = FavoriteService(db_session)
        user_a = multi_user_fixture["user_a"]
        gen_b = multi_user_fixture["gen_b"]

        # User A attempts to bookmark User B's private generation
        with pytest.raises(AuthorizationException) as exc_info:
            fav_service.add_favorite(user_id=user_a.id, generation_id=gen_b.id)
        assert exc_info.value.status_code == 403

    def test_user_a_cannot_remove_user_b_favorite(self, db_session: Session, multi_user_fixture):
        fav_service = FavoriteService(db_session)
        user_a = multi_user_fixture["user_a"]
        user_b = multi_user_fixture["user_b"]
        gen_b = multi_user_fixture["gen_b"]

        # User B bookmarks their own generation
        fav_b = fav_service.add_favorite(user_id=user_b.id, generation_id=gen_b.id)

        # User A tries to delete User B's favorite record
        with pytest.raises(AuthorizationException) as exc_info:
            fav_service.remove_favorite(favorite_id=fav_b.id, user=user_a)
        assert exc_info.value.status_code == 403

    def test_user_favorites_list_strictly_isolated(self, db_session: Session, multi_user_fixture):
        fav_service = FavoriteService(db_session)
        user_a = multi_user_fixture["user_a"]
        user_b = multi_user_fixture["user_b"]
        gen_a = multi_user_fixture["gen_a"]
        gen_b = multi_user_fixture["gen_b"]

        fav_service.add_favorite(user_id=user_a.id, generation_id=gen_a.id, label="A's favorite")
        fav_service.add_favorite(user_id=user_b.id, generation_id=gen_b.id, label="B's favorite")

        # User A listing favorites only sees A's favorites
        items_a, total_a = fav_service.list_favorites(user_id=user_a.id)
        assert total_a == 1
        assert items_a[0].generation_id == gen_a.id
        assert items_a[0].user_id == user_a.id

        # User B listing favorites only sees B's favorites
        items_b, total_b = fav_service.list_favorites(user_id=user_b.id)
        assert total_b == 1
        assert items_b[0].generation_id == gen_b.id
        assert items_b[0].user_id == user_b.id

    def test_delete_generation_cascades_and_removes_favorite(self, db_session: Session, multi_user_fixture):
        fav_service = FavoriteService(db_session)
        history_service = HistoryService(db_session)
        user_a = multi_user_fixture["user_a"]
        gen_a = multi_user_fixture["gen_a"]

        fav_a = fav_service.add_favorite(user_id=user_a.id, generation_id=gen_a.id)
        fav_id = fav_a.id

        # User A deletes their speech generation
        history_service.delete_generation(generation_id=gen_a.id, user=user_a)

        # Generation is deleted
        assert db_session.get(SpeechGeneration, gen_a.id) is None

        # Associated favorite is automatically removed via cascade (no orphan record)
        assert db_session.get(Favorite, fav_id) is None

    def test_delete_favorite_leaves_generation_intact(self, db_session: Session, multi_user_fixture):
        fav_service = FavoriteService(db_session)
        user_a = multi_user_fixture["user_a"]
        gen_a = multi_user_fixture["gen_a"]

        fav_a = fav_service.add_favorite(user_id=user_a.id, generation_id=gen_a.id)
        fav_id = fav_a.id

        # User A removes the favorite
        fav_service.remove_favorite(favorite_id=fav_id, user=user_a)

        # Favorite is removed
        assert db_session.get(Favorite, fav_id) is None

        # Underlying speech generation remains completely intact
        persisted_gen = db_session.get(SpeechGeneration, gen_a.id)
        assert persisted_gen is not None
        assert persisted_gen.id == gen_a.id
