"""
Bloop Authorization & Ownership Boundary Tests (Prompt 14 §80, §81, §83)
Verifies:
- Unauthenticated requests receive HTTP 401 Unauthorized.
- User A cannot stream or download User B's speech audio (HTTP 403 Forbidden).
- User A cannot view or delete User B's speech generation records (HTTP 403 Forbidden).
- User A cannot favorite User B's speech generation (HTTP 403 Forbidden).
- User A cannot delete User B's favorite bookmark (HTTP 403 Forbidden).
- Legitimate resource owners have full authorized access.
"""

import os
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.core.security import create_access_token
from backend.app.models.favorite import Favorite
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.user import User
from backend.app.services.audio.delivery import AudioDeliveryService


@pytest.fixture
def auth_boundary_fixture(db_session):
    """Sets up two distinct users and their isolated generation/favorite resources."""
    uid = uuid.uuid4().hex[:8]

    # User A (Alpha)
    user_a = User(
        email=f"alpha_{uid}@bloop.ai",
        hashed_password="hashed_alpha_pass_12345",
        full_name="Alpha User",
        is_active=True,
    )
    # User B (Beta)
    user_b = User(
        email=f"beta_{uid}@bloop.ai",
        hashed_password="hashed_beta_pass_12345",
        full_name="Beta User",
        is_active=True,
    )
    db_session.add(user_a)
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    # Physical audio files
    delivery = AudioDeliveryService()
    audio_data_a = b"\xff\xfb\x90\x44" * 40
    audio_data_b = b"\xff\xfb\x90\x44" * 30
    filename_a = delivery.store_temporary_audio(audio_data_a, extension="mp3")
    filename_b = delivery.store_temporary_audio(audio_data_b, extension="mp3")

    # Speech generation for User A
    gen_a = SpeechGeneration(
        user_id=user_a.id,
        text="Alpha's private confidential speech.",
        char_count=37,
        word_count=4,
        language_code="en-US",
        voice_id="normal-female",
        audio_filename=filename_a,
        duration_seconds=2.5,
        file_size_bytes=len(audio_data_a),
        provider="simulation",
        status="completed",
    )
    # Speech generation for User B
    gen_b = SpeechGeneration(
        user_id=user_b.id,
        text="Beta's private confidential speech.",
        char_count=36,
        word_count=4,
        language_code="en-US",
        voice_id="normal-female",
        audio_filename=filename_b,
        duration_seconds=2.4,
        file_size_bytes=len(audio_data_b),
        provider="simulation",
        status="completed",
    )
    db_session.add(gen_a)
    db_session.add(gen_b)
    db_session.commit()
    db_session.refresh(gen_a)
    db_session.refresh(gen_b)

    # Favorite belonging to User B
    fav_b = Favorite(
        user_id=user_b.id,
        generation_id=gen_b.id,
        label="Beta Favorite",
    )
    db_session.add(fav_b)
    db_session.commit()
    db_session.refresh(fav_b)

    token_a = create_access_token(subject=str(user_a.id))
    token_b = create_access_token(subject=str(user_b.id))

    yield {
        "user_a": user_a,
        "user_b": user_b,
        "token_a": token_a,
        "token_b": token_b,
        "gen_a": gen_a,
        "gen_b": gen_b,
        "fav_b": fav_b,
        "filename_a": filename_a,
        "filename_b": filename_b,
    }

    # Teardown
    try:
        delivery.delete_audio_file(filename_a)
        delivery.delete_audio_file(filename_b)
        db_session.delete(fav_b)
        db_session.delete(gen_a)
        db_session.delete(gen_b)
        db_session.delete(user_a)
        db_session.delete(user_b)
        db_session.commit()
    except Exception:
        db_session.rollback()


class TestAuthorizationBoundary:
    """Verifies user ownership isolation across all protected Bloop resources."""

    def test_unauthenticated_protected_endpoints_return_401(self, client: TestClient):
        # 1. Unauthenticated TTS generation
        res_tts = client.post("/api/v1/tts", json={"text": "Test speech", "voice_id": "v1", "language": "en-US"})
        assert res_tts.status_code == 401
        assert res_tts.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

        # 2. Unauthenticated audio streaming
        res_audio = client.get("/api/v1/tts/1/audio")
        assert res_audio.status_code == 401

        # 3. Unauthenticated audio download
        res_dl = client.get("/api/v1/tts/1/download")
        assert res_dl.status_code == 401

        # 4. Unauthenticated history
        res_hist = client.get("/api/v1/history")
        assert res_hist.status_code == 401

        # 5. Unauthenticated favorites
        res_fav = client.get("/api/v1/favorites")
        assert res_fav.status_code == 401

        # 6. Unauthenticated quantum text
        res_q = client.post("/api/v1/quantum/text", json={"text": "Hello"})
        assert res_q.status_code == 401

    def test_user_a_cannot_access_user_b_audio(self, client: TestClient, auth_boundary_fixture):
        data = auth_boundary_fixture
        token_a = data["token_a"]
        gen_b = data["gen_b"]

        # User A attempts to stream User B's audio
        res_stream = client.get(
            f"/api/v1/tts/{gen_b.id}/audio",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_stream.status_code == 403
        assert res_stream.json()["error"]["code"] == "GENERATION_ACCESS_DENIED"

        # User A attempts to download User B's audio
        res_dl = client.get(
            f"/api/v1/tts/{gen_b.id}/download",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_dl.status_code == 403
        assert res_dl.json()["error"]["code"] == "GENERATION_ACCESS_DENIED"

    def test_user_a_can_access_own_audio(self, client: TestClient, auth_boundary_fixture):
        data = auth_boundary_fixture
        token_a = data["token_a"]
        gen_a = data["gen_a"]

        res_stream = client.get(
            f"/api/v1/tts/{gen_a.id}/audio",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_stream.status_code == 200

        res_dl = client.get(
            f"/api/v1/tts/{gen_a.id}/download",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_dl.status_code == 200

    def test_user_a_cannot_view_or_delete_user_b_history(self, client: TestClient, auth_boundary_fixture):
        data = auth_boundary_fixture
        token_a = data["token_a"]
        gen_b = data["gen_b"]

        # View User B's record
        res_view = client.get(
            f"/api/v1/history/{gen_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_view.status_code == 403
        assert res_view.json()["error"]["code"] == "FORBIDDEN"

        # Delete User B's record
        res_del = client.delete(
            f"/api/v1/history/{gen_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_del.status_code == 403

    def test_user_a_cannot_favorite_user_b_generation(self, client: TestClient, auth_boundary_fixture):
        data = auth_boundary_fixture
        token_a = data["token_a"]
        gen_b = data["gen_b"]

        # User A tries to favorite User B's generation
        res = client.post(
            "/api/v1/favorites",
            json={"generation_id": gen_b.id, "label": "Stolen Favorite"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 403
        assert "permission" in res.json()["error"]["message"].lower()

    def test_user_a_cannot_delete_user_b_favorite(self, client: TestClient, auth_boundary_fixture):
        data = auth_boundary_fixture
        token_a = data["token_a"]
        fav_b = data["fav_b"]

        res = client.delete(
            f"/api/v1/favorites/{fav_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 403
