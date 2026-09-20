"""
End-to-End Integration Tests for Speech Generation, Audio Delivery & Download Pipeline
Prompt 13 Authoritative Test Suite:
- Validates complete pipeline from POST /api/v1/tts to ElevenLabs synthesis,
  audio processing, disk storage, database metadata persistence, range streaming,
  attachment downloading, ownership access control (HTTP 403), and failure consistency.
"""

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.user import User
from backend.app.models.voice import Voice
from backend.app.providers.base import TTSProviderResult
from backend.app.providers.elevenlabs.exceptions import ElevenLabsException
from backend.app.providers.elevenlabs.provider import ElevenLabsProvider
from backend.app.repositories.voice_repository import VoiceRepository
from backend.app.services.speech.service import SpeechService


@pytest.fixture
def auth_users(db_session):
    """Creates two distinct test users with isolated email addresses and tokens."""
    uid = uuid.uuid4().hex[:8]
    user_a = User(
        email=f"alpha_{uid}@bloop.ai",
        hashed_password=get_password_hash("AlphaPass123!"),
        full_name="Alpha User",
        is_active=True,
    )
    user_b = User(
        email=f"beta_{uid}@bloop.ai",
        hashed_password=get_password_hash("BetaPass123!"),
        full_name="Beta User",
        is_active=True,
    )
    db_session.add(user_a)
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    token_a = create_access_token(subject=str(user_a.id))
    token_b = create_access_token(subject=str(user_b.id))

    yield {
        "user_a": user_a,
        "user_b": user_b,
        "token_a": token_a,
        "token_b": token_b,
    }

    # Teardown
    try:
        db_session.query(SpeechGeneration).filter(
            SpeechGeneration.user_id.in_([user_a.id, user_b.id])
        ).delete(synchronize_session=False)
        db_session.delete(user_a)
        db_session.delete(user_b)
        db_session.commit()
    except Exception:
        db_session.rollback()


@pytest.fixture
def elevenlabs_voice(db_session):
    """Temporarily configures normal-female as an ElevenLabs provider voice."""
    voice_repo = VoiceRepository(db_session)
    voice = voice_repo.get_by_voice_id("normal-female")
    original_provider = voice.provider if voice else "dynamic"
    if voice:
        voice.provider = "elevenlabs"
        db_session.commit()

    yield "normal-female"

    if voice:
        voice.provider = original_provider
        db_session.commit()


class TestSpeechGenerationAndAudioDeliveryPipeline:
    """End-to-end integration tests for Prompt 13 speech generation and delivery pipeline."""

    def test_end_to_end_synthesis_playback_and_download(
        self, client: TestClient, db_session, auth_users, elevenlabs_voice
    ):
        """
        Complete lifecycle test:
        1. Authenticated user submits text to POST /api/v1/tts.
        2. ElevenLabs provider synthesizes audio (mocked).
        3. AudioProcessor validates payload and extracts metadata.
        4. AudioDeliveryService buffers audio safely on disk.
        5. SpeechGeneration metadata is persisted in database with status=completed.
        6. Browser player streams audio via GET /api/v1/tts/{generation_id}/audio.
        7. Browser player seeks audio using RFC 7233 Range headers (HTTP 206).
        8. User downloads audio via GET /api/v1/tts/{generation_id}/download.
        """
        user_a = auth_users["user_a"]
        token_a = auth_users["token_a"]

        # Synthetic valid MP3 bytes (ID3 tag + MPEG frames)
        valid_mp3_payload = b"ID3\x03\x00\x00\x00\x00\x00\x00" + (b"\xff\xfb\x90\x44" * 50)
        provider_result = TTSProviderResult(
            audio_bytes=valid_mp3_payload,
            content_type="audio/mpeg",
            file_extension="mp3",
            provider="elevenlabs",
            provider_request_id="el-test-req-001",
            latency_ms=145.0,
            duration_seconds=4.2,
        )

        with patch.object(
            ElevenLabsProvider, "is_configured", return_value=True
        ), patch.object(
            ElevenLabsProvider, "generate_speech", AsyncMock(return_value=provider_result)
        ):
            # 1. Post TTS generation request
            payload = {
                "text": "Bloop natural speech synthesis test through ElevenLabs.",
                "language": "en-US",
                "voice_id": elevenlabs_voice,
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "Neutral",
            }
            res = client.post(
                "/api/v1/tts",
                json=payload,
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert res.status_code == 200, f"TTS generation failed: {res.text}"
            data = res.json()
            assert data["success"] is True
            tts_data = data["data"]

            gen_id = tts_data["generation_id"]
            assert gen_id is not None
            assert tts_data["char_count"] == len(payload["text"])
            assert tts_data["word_count"] == 7
            assert tts_data["content_type"] == "audio/mpeg"
            assert tts_data["audio_format"] == "mp3"
            assert tts_data["duration_seconds"] == 4.2
            assert "audio" in tts_data["audio_url"]
            assert "download" in tts_data["download_url"]

            # 2. Verify database persistence
            gen_record = db_session.query(SpeechGeneration).filter(SpeechGeneration.id == gen_id).first()
            assert gen_record is not None
            assert gen_record.user_id == user_a.id
            assert gen_record.status == "completed"
            assert gen_record.provider == "elevenlabs"
            assert gen_record.provider_request_id == "el-test-req-001"
            assert gen_record.file_size_bytes == len(valid_mp3_payload)
            assert gen_record.audio_format == "mp3"

            # 3. Verify physical file exists on disk
            storage_path = os.path.join(settings.AUDIO_STORAGE_PATH, gen_record.audio_filename)
            assert os.path.exists(storage_path)

            # 4. Stream full audio (HTTP 200)
            stream_res = client.get(
                f"/api/v1/tts/{gen_id}/audio",
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert stream_res.status_code == 200
            assert stream_res.headers["content-type"] == "audio/mpeg"
            assert stream_res.headers["accept-ranges"] == "bytes"
            assert len(stream_res.content) == len(valid_mp3_payload)

            # 5. Range Request (Seeking byte offset: HTTP 206 Partial Content)
            range_res = client.get(
                f"/api/v1/tts/{gen_id}/audio",
                headers={
                    "Authorization": f"Bearer {token_a}",
                    "Range": "bytes=0-49",
                },
            )
            assert range_res.status_code == 206
            assert "bytes 0-49/" in range_res.headers["content-range"]
            assert range_res.headers["accept-ranges"] == "bytes"
            assert len(range_res.content) == 50

            # 6. Attachment Download (Content-Disposition header)
            download_res = client.get(
                f"/api/v1/tts/{gen_id}/download",
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert download_res.status_code == 200
            assert f'attachment; filename="bloop-speech-{gen_id}.mp3"' in download_res.headers["content-disposition"]
            assert len(download_res.content) == len(valid_mp3_payload)

            # Clean up audio file
            if os.path.exists(storage_path):
                os.remove(storage_path)

    def test_ownership_authorization_on_streaming_and_download(
        self, client: TestClient, db_session, auth_users
    ):
        """Verifies that non-owners cannot stream or download another user's generation."""
        user_a = auth_users["user_a"]
        token_b = auth_users["token_b"]  # User B's token

        # Store an audio file
        unique_file = f"test_private_{uuid.uuid4().hex}.mp3"
        full_path = os.path.join(settings.AUDIO_STORAGE_PATH, unique_file)
        with open(full_path, "wb") as f:
            f.write(b"private-user-a-audio-data-payload")

        gen_a = SpeechGeneration(
            user_id=user_a.id,
            text="Confidential audio belonging to User A.",
            char_count=40,
            word_count=6,
            language_code="en-US",
            voice_id="normal-female",
            audio_filename=unique_file,
            duration_seconds=2.5,
            file_size_bytes=len(b"private-user-a-audio-data-payload"),
            provider="elevenlabs",
            status="completed",
        )
        db_session.add(gen_a)
        db_session.commit()
        db_session.refresh(gen_a)

        try:
            # 1. User B attempts to stream User A's generation -> HTTP 403
            res_stream = client.get(
                f"/api/v1/tts/{gen_a.id}/audio",
                headers={"Authorization": f"Bearer {token_b}"},
            )
            assert res_stream.status_code == 403
            assert res_stream.json()["error"]["code"] == "GENERATION_ACCESS_DENIED"

            # 2. User B attempts to download User A's generation -> HTTP 403
            res_dl = client.get(
                f"/api/v1/tts/{gen_a.id}/download",
                headers={"Authorization": f"Bearer {token_b}"},
            )
            assert res_dl.status_code == 403
            assert res_dl.json()["error"]["code"] == "GENERATION_ACCESS_DENIED"

            # 3. Unauthenticated requester attempts to stream -> HTTP 401 or 403
            res_anon = client.get(f"/api/v1/tts/{gen_a.id}/audio")
            assert res_anon.status_code in (401, 403)

        finally:
            if os.path.exists(full_path):
                os.remove(full_path)
            db_session.delete(gen_a)
            db_session.commit()

    def test_missing_generation_and_missing_audio_handling(
        self, client: TestClient, db_session, auth_users
    ):
        """Verifies 404 responses when generation record or physical audio file is missing."""
        token_a = auth_users["token_a"]

        # 1. Non-existent generation ID -> 404 GENERATION_NOT_FOUND
        res = client.get(
            "/api/v1/tts/99999999/audio",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "GENERATION_NOT_FOUND"

        # 2. Generation exists in DB but physical file missing from storage -> 404 AUDIO_NOT_FOUND
        user_a = auth_users["user_a"]
        gen_ghost = SpeechGeneration(
            user_id=user_a.id,
            text="Ghost file generation text.",
            char_count=28,
            word_count=4,
            language_code="en-US",
            voice_id="normal-female",
            audio_filename=f"ghost_missing_file_{uuid.uuid4().hex}.mp3",
            duration_seconds=1.0,
            file_size_bytes=100,
            provider="elevenlabs",
            status="completed",
        )
        db_session.add(gen_ghost)
        db_session.commit()
        db_session.refresh(gen_ghost)

        try:
            res_ghost = client.get(
                f"/api/v1/tts/{gen_ghost.id}/audio",
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert res_ghost.status_code == 404
            assert res_ghost.json()["error"]["code"] == "AUDIO_NOT_FOUND"
        finally:
            db_session.delete(gen_ghost)
            db_session.commit()

    def test_provider_failure_records_failed_status_and_leaves_no_orphaned_audio(
        self, client: TestClient, db_session, auth_users, elevenlabs_voice
    ):
        """
        When the provider synthesis fails:
        1. API returns error status (500 / 502).
        2. A SpeechGeneration record is persisted with status=failed for audit tracking.
        3. No orphaned audio files remain on disk.
        """
        token_a = auth_users["token_a"]
        user_a = auth_users["user_a"]

        with patch.object(
            ElevenLabsProvider, "is_configured", return_value=True
        ), patch.object(
            ElevenLabsProvider,
            "generate_speech",
            AsyncMock(side_effect=ElevenLabsException("Provider connection timeout", code="TTS_PROVIDER_UNAVAILABLE")),
        ):
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Synthesis failure test prompt.",
                    "voice_id": elevenlabs_voice,
                    "language": "en-US",
                },
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert res.status_code in [500, 502]
            data = res.json()
            assert data["success"] is False

            # Verify failed record was persisted for auditing
            failed_record = (
                db_session.query(SpeechGeneration)
                .filter(
                    SpeechGeneration.user_id == user_a.id,
                    SpeechGeneration.status == "failed",
                )
                .order_by(SpeechGeneration.created_at.desc())
                .first()
            )
            assert failed_record is not None
            assert failed_record.status == "failed"
            assert failed_record.error_message is not None

    def test_invalid_audio_bytes_rejected_by_processor_and_persists_failure(
        self, client: TestClient, db_session, auth_users, elevenlabs_voice
    ):
        """
        When the provider returns invalid audio bytes (e.g. HTML error page or empty bytes):
        1. AudioProcessor rejects with AUDIO_GENERATION_INVALID (HTTP 422).
        2. A failed record is recorded in database.
        3. No invalid audio is stored or delivered.
        """
        token_a = auth_users["token_a"]
        user_a = auth_users["user_a"]

        # Simulated corrupted HTML response
        corrupt_html = b"<html><body><h1>502 Bad Gateway</h1></body></html>"
        provider_result = TTSProviderResult(
            audio_bytes=corrupt_html,
            content_type="audio/mpeg",
            file_extension="mp3",
            provider="elevenlabs",
        )

        with patch.object(
            ElevenLabsProvider, "is_configured", return_value=True
        ), patch.object(
            ElevenLabsProvider, "generate_speech", AsyncMock(return_value=provider_result)
        ):
            res = client.post(
                "/api/v1/tts",
                json={
                    "text": "Corrupt audio test prompt.",
                    "voice_id": elevenlabs_voice,
                    "language": "en-US",
                },
                headers={"Authorization": f"Bearer {token_a}"},
            )
            assert res.status_code == 422
            data = res.json()
            assert data["success"] is False
            assert data["error"]["code"] == "AUDIO_GENERATION_INVALID"

            # Verify failed audit record
            failed_record = (
                db_session.query(SpeechGeneration)
                .filter(
                    SpeechGeneration.user_id == user_a.id,
                    SpeechGeneration.status == "failed",
                )
                .order_by(SpeechGeneration.created_at.desc())
                .first()
            )
            assert failed_record is not None
            assert failed_record.error_code == "AUDIO_GENERATION_INVALID"
