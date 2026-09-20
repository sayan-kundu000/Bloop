"""
Bloop History Security & Ownership Isolation Automated Tests
Validates strict user data isolation, cross-user denial (HTTP 403),
unauthenticated access rejection (HTTP 401), and server-enforced ownership (Prompt 15 §18-19 & §45).
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.services.auth.jwt import create_access_token
from backend.app.services.audio.delivery import AudioDeliveryService


@pytest.fixture
def multi_user_fixture(db_session: Session):
    """Creates two distinct isolated users with corresponding generation records."""
    user_a = User(
        email=f"user_a_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass_a",
        full_name="User Alpha",
        is_active=True,
    )
    user_b = User(
        email=f"user_b_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_pass_b",
        full_name="User Beta",
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    delivery = AudioDeliveryService()
    valid_mp3 = b"\xff\xfb\x90\x44" + b"\x00" * 200

    filename_a = delivery.store_temporary_audio(valid_mp3, "mp3")
    filename_b = delivery.store_temporary_audio(valid_mp3, "mp3")

    gen_a = SpeechGeneration(
        user_id=user_a.id,
        text="User Alpha private synthesis record",
        char_count=36,
        word_count=5,
        language_code="en-US",
        voice_id="v-alpha",
        audio_filename=filename_a,
        duration_seconds=2.5,
        file_size_bytes=len(valid_mp3),
        status="completed",
    )
    gen_b = SpeechGeneration(
        user_id=user_b.id,
        text="User Beta confidential synthesis record",
        char_count=40,
        word_count=5,
        language_code="en-US",
        voice_id="v-beta",
        audio_filename=filename_b,
        duration_seconds=3.0,
        file_size_bytes=len(valid_mp3),
        status="completed",
    )
    db_session.add_all([gen_a, gen_b])
    db_session.commit()
    db_session.refresh(gen_a)
    db_session.refresh(gen_b)

    token_a = create_access_token(subject=str(user_a.id))
    token_b = create_access_token(subject=str(user_b.id))

    yield {
        "user_a": user_a,
        "user_b": user_b,
        "gen_a": gen_a,
        "gen_b": gen_b,
        "token_a": token_a,
        "token_b": token_b,
        "filename_a": filename_a,
        "filename_b": filename_b,
    }

    # Teardown
    delivery.delete_audio_file(filename_a)
    delivery.delete_audio_file(filename_b)


class TestHistoryIsolationAndSecurity:
    """Security tests verifying user data isolation across all history operations."""

    def test_unauthenticated_history_requests_rejected_with_401(self, client: TestClient):
        # List history
        res_list = client.get("/api/v1/history")
        assert res_list.status_code == 401
        assert res_list.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

        # History detail
        res_detail = client.get("/api/v1/history/1")
        assert res_detail.status_code == 401
        assert res_detail.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

        # History deletion
        res_del = client.delete("/api/v1/history/1")
        assert res_del.status_code == 401
        assert res_del.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_user_a_cannot_see_user_b_history_in_list(
        self, client: TestClient, multi_user_fixture: dict
    ):
        token_a = multi_user_fixture["token_a"]
        gen_a = multi_user_fixture["gen_a"]
        gen_b = multi_user_fixture["gen_b"]

        res = client.get(
            "/api/v1/history",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        items = data["items"]
        item_ids = [item["id"] for item in items]

        assert gen_a.id in item_ids
        assert gen_b.id not in item_ids
        # Explicit check that no returned items belong to user B
        for item in items:
            assert item["user_id"] == multi_user_fixture["user_a"].id

    def test_user_a_cannot_access_user_b_generation_detail_returns_403(
        self, client: TestClient, multi_user_fixture: dict
    ):
        token_a = multi_user_fixture["token_a"]
        gen_b = multi_user_fixture["gen_b"]

        res = client.get(
            f"/api/v1/history/{gen_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 403
        error = res.json()["error"]
        assert error["code"] in ("FORBIDDEN", "ACCESS_DENIED")

    def test_user_a_cannot_delete_user_b_generation_returns_403(
        self, client: TestClient, multi_user_fixture: dict
    ):
        token_a = multi_user_fixture["token_a"]
        gen_b = multi_user_fixture["gen_b"]

        res = client.delete(
            f"/api/v1/history/{gen_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 403
        error = res.json()["error"]
        assert error["code"] in ("FORBIDDEN", "ACCESS_DENIED")

    def test_client_cannot_override_user_id_via_query_params(
        self, client: TestClient, multi_user_fixture: dict
    ):
        token_a = multi_user_fixture["token_a"]
        user_b = multi_user_fixture["user_b"]
        gen_b = multi_user_fixture["gen_b"]

        # Even if a malicious client attempts to pass user_id in query params
        res = client.get(
            f"/api/v1/history?user_id={user_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        item_ids = [item["id"] for item in items]
        assert gen_b.id not in item_ids
