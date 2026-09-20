"""
Unit Tests for Audio Processor & Audio Delivery Services
Tests validation of magic headers (MP3/WAV), rejection of corrupt payloads,
ownership access control, range streaming, and lifecycle file pruning.
"""

import os
import time
from unittest.mock import MagicMock
import pytest

from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.user import User
from backend.app.providers.base import TTSProviderResult
from backend.app.services.audio.delivery import AudioDeliveryService
from backend.app.services.audio.exceptions import (
    AudioGenerationInvalidException,
    AudioNotFoundException,
    GenerationAccessDeniedException,
    GenerationNotFoundException,
)
from backend.app.services.audio.processor import AudioProcessor


class TestAudioProcessor:
    """Unit tests for AudioProcessor validation and normalization."""

    def setup_method(self):
        self.processor = AudioProcessor()

    def test_processor_valid_mp3_magic_bytes(self):
        # Synthetic valid MP3 with ID3 header
        id3_header = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\xff\xfb\x90\x44" * 10
        processed = self.processor.process(id3_header, fallback_duration=3.5)
        assert processed.metadata.audio_format == "mp3"
        assert processed.metadata.content_type == "audio/mpeg"
        assert processed.metadata.file_extension == "mp3"
        assert processed.metadata.file_size_bytes == len(id3_header)
        assert processed.metadata.duration_seconds == 3.5

    def test_processor_valid_wav_magic_bytes(self):
        # Synthetic valid RIFF WAVE header (44 bytes standard PCM header)
        riff_header = (
            b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        )
        processed = self.processor.process(riff_header)
        assert processed.metadata.audio_format == "wav"
        assert processed.metadata.content_type == "audio/wav"
        assert processed.metadata.file_extension == "wav"

    def test_processor_rejects_empty_bytes(self):
        with pytest.raises(AudioGenerationInvalidException) as exc_info:
            self.processor.process(b"")
        assert "empty" in str(exc_info.value).lower()

    def test_processor_rejects_truncated_bytes(self):
        with pytest.raises(AudioGenerationInvalidException) as exc_info:
            self.processor.process(b"short")
        assert "truncated" in str(exc_info.value).lower()

    def test_processor_rejects_html_or_json_error_text(self):
        # Simulated provider returning JSON error instead of audio bytes
        error_json = b'{"error": "Internal Server Error", "code": 500}'
        with pytest.raises(AudioGenerationInvalidException) as exc_info:
            self.processor.process(error_json)
        assert "textual" in str(exc_info.value).lower() or "document" in str(exc_info.value).lower()

    def test_processor_normalizes_tts_provider_result(self):
        provider_res = TTSProviderResult(
            audio_bytes=b"\xff\xfb\x90\x44" * 15,
            content_type="audio/mpeg",
            file_extension="mp3",
            duration_seconds=5.0,
            provider="elevenlabs",
        )
        processed = self.processor.process(provider_res)
        assert processed.metadata.audio_format == "mp3"
        assert processed.metadata.duration_seconds == 5.0
        assert processed.metadata.file_size_bytes == len(provider_res.audio_bytes)


class TestAudioDeliveryService:
    """Unit tests for AudioDeliveryService storage, access control, and cleanup."""

    @pytest.fixture
    def delivery_service(self, tmp_path):
        storage_dir = str(tmp_path / "audio_test")
        return AudioDeliveryService(storage_path=storage_dir)

    def test_delivery_stores_temporary_audio(self, delivery_service):
        audio_content = b"\xff\xfb\x90\x44" * 20
        filename = delivery_service.store_temporary_audio(audio_content, extension="mp3")
        assert filename.endswith(".mp3")

        expected_path = os.path.join(delivery_service.storage_path, filename)
        assert os.path.exists(expected_path)
        with open(expected_path, "rb") as f:
            assert f.read() == audio_content

    def test_delivery_resolves_audio_for_owner(self, delivery_service, db_session):
        # Store file on disk
        audio_content = b"\xff\xfb\x90\x44" * 20
        filename = delivery_service.store_temporary_audio(audio_content, extension="mp3")

        # Create generation owned by user 42
        gen = SpeechGeneration(
            user_id=42,
            text="Ownership test text.",
            char_count=20,
            word_count=3,
            language_code="en-US",
            voice_id="normal-female",
            audio_filename=filename,
            duration_seconds=2.0,
            file_size_bytes=len(audio_content),
            provider="elevenlabs",
            status="completed",
        )
        db_session.add(gen)
        db_session.commit()
        db_session.refresh(gen)

        # Owner 42 can resolve
        path, resolved_gen = delivery_service.resolve_audio_file(
            identifier=gen.id,
            user_id=42,
            db=db_session,
        )
        assert path == os.path.join(delivery_service.storage_path, filename)
        assert resolved_gen.id == gen.id

    def test_delivery_rejects_non_owner_with_403(self, delivery_service, db_session):
        audio_content = b"\xff\xfb\x90\x44" * 20
        filename = delivery_service.store_temporary_audio(audio_content, extension="mp3")

        gen = SpeechGeneration(
            user_id=100,  # Owned by user 100
            text="Private user text.",
            char_count=18,
            word_count=3,
            language_code="en-US",
            voice_id="normal-female",
            audio_filename=filename,
            duration_seconds=1.5,
            file_size_bytes=len(audio_content),
            provider="elevenlabs",
            status="completed",
        )
        db_session.add(gen)
        db_session.commit()
        db_session.refresh(gen)

        # User 200 attempts to access User 100's generation -> HTTP 403
        with pytest.raises(GenerationAccessDeniedException) as exc_info:
            delivery_service.resolve_audio_file(
                identifier=gen.id,
                user_id=200,
                db=db_session,
            )
        assert exc_info.value.status_code == 403

    def test_delivery_raises_404_for_missing_generation(self, delivery_service, db_session):
        with pytest.raises(GenerationNotFoundException) as exc_info:
            delivery_service.resolve_audio_file(
                identifier=999999,
                user_id=1,
                db=db_session,
            )
        assert exc_info.value.status_code == 404

    def test_delivery_raises_404_for_missing_file_on_disk(self, delivery_service, db_session):
        gen = SpeechGeneration(
            user_id=1,
            text="Ghost file text.",
            char_count=16,
            word_count=3,
            language_code="en-US",
            voice_id="normal-female",
            audio_filename="nonexistent_ghost_file.mp3",
            duration_seconds=1.0,
            file_size_bytes=100,
            provider="elevenlabs",
            status="completed",
        )
        db_session.add(gen)
        db_session.commit()
        db_session.refresh(gen)

        with pytest.raises(AudioNotFoundException) as exc_info:
            delivery_service.resolve_audio_file(
                identifier=gen.id,
                user_id=1,
                db=db_session,
            )
        assert exc_info.value.status_code == 404

    def test_delivery_cleanup_expired_audio(self, delivery_service):
        old_file = os.path.join(delivery_service.storage_path, "old_expired.mp3")
        with open(old_file, "wb") as f:
            f.write(b"expired-audio-data")

        # Fake old timestamp (48 hours ago)
        old_time = time.time() - (48 * 3600)
        os.utime(old_file, (old_time, old_time))

        new_file = os.path.join(delivery_service.storage_path, "new_active.mp3")
        with open(new_file, "wb") as f:
            f.write(b"active-audio-data")

        pruned = delivery_service.cleanup_expired_audio(max_age_hours=24)
        assert pruned == 1
        assert not os.path.exists(old_file)
        assert os.path.exists(new_file)
