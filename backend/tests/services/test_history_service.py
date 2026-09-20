"""
Bloop Speech History Service Automated Tests
Validates pagination, multi-column search, language/status filtering,
controlled sorting allowlist, detail inspection, and asset deletion (Prompt 15 §20-26).
"""

import os
import uuid
import pytest
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.favorite import Favorite
from backend.app.services.history.service import HistoryService
from backend.app.services.audio.delivery import AudioDeliveryService
from backend.app.schemas.history import HistoryQueryFilter
from backend.app.core.exceptions import (
    ResourceNotFoundException,
    AuthorizationException,
    ValidationException,
)


@pytest.fixture
def history_fixture(db_session: Session):
    """Creates a user and multiple generations with various attributes for testing."""
    user = User(
        email=f"history_test_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass",
        full_name="History Tester",
        is_active=True,
    )
    other_user = User(
        email=f"history_other_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass",
        full_name="Other User",
        is_active=True,
    )
    db_session.add(user)
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(other_user)

    delivery = AudioDeliveryService()
    valid_mp3 = b"\xff\xfb\x90\x44" + b"\x00" * 400

    filename_1 = delivery.store_temporary_audio(valid_mp3, "mp3")
    filename_2 = delivery.store_temporary_audio(valid_mp3, "mp3")
    filename_3 = delivery.store_temporary_audio(valid_mp3, "mp3")
    filename_other = delivery.store_temporary_audio(valid_mp3, "mp3")

    # User generations
    gen_1 = SpeechGeneration(
        user_id=user.id,
        text="Quantum algorithm speech synthesis alpha",
        char_count=40,
        word_count=5,
        language_code="en-US",
        voice_id="v-alpha",
        voice_name="Alpha Voice",
        audio_filename=filename_1,
        duration_seconds=3.5,
        file_size_bytes=len(valid_mp3),
        status="completed",
    )
    gen_2 = SpeechGeneration(
        user_id=user.id,
        text="Spanish text synthesis prueba beta",
        char_count=35,
        word_count=5,
        language_code="es-ES",
        voice_id="v-beta",
        voice_name="Beta Voice",
        audio_filename=filename_2,
        duration_seconds=6.0,
        file_size_bytes=len(valid_mp3),
        status="completed",
    )
    gen_3 = SpeechGeneration(
        user_id=user.id,
        text="Failed synthesis attempt due to network",
        char_count=38,
        word_count=6,
        language_code="en-US",
        voice_id="v-gamma",
        voice_name="Gamma Voice",
        audio_filename=filename_3,
        duration_seconds=0.0,
        file_size_bytes=0,
        status="failed",
    )

    # Other user generation
    gen_other = SpeechGeneration(
        user_id=other_user.id,
        text="Other user secret private audio text",
        char_count=36,
        word_count=6,
        language_code="en-US",
        voice_id="v-other",
        audio_filename=filename_other,
        duration_seconds=2.0,
        file_size_bytes=len(valid_mp3),
        status="completed",
    )

    db_session.add_all([gen_1, gen_2, gen_3, gen_other])
    db_session.commit()
    for g in [gen_1, gen_2, gen_3, gen_other]:
        db_session.refresh(g)

    # Bookmark gen_1 as favorite
    fav = Favorite(user_id=user.id, generation_id=gen_1.id)
    db_session.add(fav)
    db_session.commit()

    yield {
        "user": user,
        "other_user": other_user,
        "gen_1": gen_1,
        "gen_2": gen_2,
        "gen_3": gen_3,
        "gen_other": gen_other,
        "filenames": [filename_1, filename_2, filename_3, filename_other],
    }

    # Teardown
    for fn in [filename_1, filename_2, filename_3, filename_other]:
        delivery.delete_audio_file(fn)


class TestHistoryService:
    """Tests for HistoryService querying, filtering, and deletion."""

    def test_list_history_scoped_to_user_only(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]

        filter_params = HistoryQueryFilter()
        items, total = service.list_history(user.id, filter_params)

        assert total == 3
        assert len(items) == 3
        # Check that none belong to other user
        item_ids = [item.id for item in items]
        assert history_fixture["gen_other"].id not in item_ids
        assert history_fixture["gen_1"].id in item_ids
        assert history_fixture["gen_2"].id in item_ids
        assert history_fixture["gen_3"].id in item_ids

        # Verify gen_1 is marked as favorite
        gen_1_item = next(i for i in items if i.id == history_fixture["gen_1"].id)
        assert gen_1_item.is_favorite is True
        assert gen_1_item.favorite_id is not None

    def test_list_history_search_filter(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]

        # Search by text keyword
        filter_quantum = HistoryQueryFilter(search="quantum")
        items, total = service.list_history(user.id, filter_quantum)
        assert total == 1
        assert items[0].id == history_fixture["gen_1"].id

        # Search by voice name
        filter_voice = HistoryQueryFilter(search="Beta Voice")
        items, total = service.list_history(user.id, filter_voice)
        assert total == 1
        assert items[0].id == history_fixture["gen_2"].id

    def test_list_history_language_and_status_filter(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]

        # Language filter: es-ES
        filter_lang = HistoryQueryFilter(language="es-ES")
        items, total = service.list_history(user.id, filter_lang)
        assert total == 1
        assert items[0].language_code == "es-ES"

        # Status filter: failed
        filter_failed = HistoryQueryFilter(status="failed")
        items, total = service.list_history(user.id, filter_failed)
        assert total == 1
        assert items[0].status == "failed"

    def test_list_history_sorting_allowlist(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]

        # Sort by duration_seconds desc
        filter_duration = HistoryQueryFilter(sort_by="duration_seconds", order="desc")
        items, _ = service.list_history(user.id, filter_duration)
        # Expected: gen_2 (6.0s) first, then gen_1 (3.5s), then gen_3 (0.0s)
        assert items[0].id == history_fixture["gen_2"].id
        assert items[1].id == history_fixture["gen_1"].id
        assert items[2].id == history_fixture["gen_3"].id

    def test_list_history_bounded_pagination(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]

        filter_page1 = HistoryQueryFilter(page=1, page_size=2)
        items_p1, total = service.list_history(user.id, filter_page1)
        assert total == 3
        assert len(items_p1) == 2

        filter_page2 = HistoryQueryFilter(page=2, page_size=2)
        items_p2, total2 = service.list_history(user.id, filter_page2)
        assert total2 == 3
        assert len(items_p2) == 1

    def test_get_generation_detail_owner(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]
        gen_1 = history_fixture["gen_1"]

        detail = service.get_generation_detail(gen_1.id, user)
        assert detail.id == gen_1.id
        assert detail.text == gen_1.text
        assert detail.audio_url.endswith(gen_1.audio_filename)
        assert detail.download_url.endswith(gen_1.audio_filename)
        assert detail.is_favorite is True

    def test_get_generation_detail_missing_raises_404(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]

        with pytest.raises(ResourceNotFoundException):
            service.get_generation_detail(999999, user)

    def test_delete_generation_owner_cleans_audio_file(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]
        gen_2 = history_fixture["gen_2"]
        filename = gen_2.audio_filename

        delivery = AudioDeliveryService()
        file_path = os.path.join(delivery.storage_path, filename)
        assert os.path.exists(file_path)

        success = service.delete_generation(gen_2.id, user)
        assert success is True

        # Verify DB record is deleted
        db_gen = db_session.query(SpeechGeneration).filter(SpeechGeneration.id == gen_2.id).first()
        assert db_gen is None

        # Verify audio file removed from disk
        assert not os.path.exists(file_path)

    def test_list_history_favorite_filter(
        self, db_session: Session, history_fixture: dict
    ):
        service = HistoryService(db_session)
        user = history_fixture["user"]
        gen_1 = history_fixture["gen_1"]

        # gen_1 was favorited in fixture
        filter_fav = HistoryQueryFilter(favorite=True)
        items, total = service.list_history(user.id, filter_fav)
        assert total == 1
        assert items[0].id == gen_1.id
        assert items[0].is_favorite is True

        # Non-favorited items
        filter_non_fav = HistoryQueryFilter(favorite=False)
        items_non, total_non = service.list_history(user.id, filter_non_fav)
        assert total_non == 2
        for item in items_non:
            assert item.is_favorite is False

    def test_list_history_date_range_filters(
        self, db_session: Session, history_fixture: dict
    ):
        from datetime import datetime, timezone, timedelta

        service = HistoryService(db_session)
        user = history_fixture["user"]

        now = datetime.now(timezone.utc)
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)

        # Filter within range [past, future]
        filter_valid = HistoryQueryFilter(created_after=past, created_before=future)
        items, total = service.list_history(user.id, filter_valid)
        assert total == 3

        # Filter in distant past [past - 10d, past - 5d]
        filter_empty = HistoryQueryFilter(
            created_after=now - timedelta(days=10),
            created_before=now - timedelta(days=5),
        )
        empty_items, empty_total = service.list_history(user.id, filter_empty)
        assert empty_total == 0

    def test_list_history_invalid_date_range_raises_validation_exception(
        self, db_session: Session, history_fixture: dict
    ):
        from datetime import datetime, timezone, timedelta

        service = HistoryService(db_session)
        user = history_fixture["user"]

        now = datetime.now(timezone.utc)
        # created_after > created_before
        invalid_filter = HistoryQueryFilter(
            created_after=now + timedelta(days=1),
            created_before=now - timedelta(days=1),
        )

        with pytest.raises(ValidationException):
            service.list_history(user.id, invalid_filter)
