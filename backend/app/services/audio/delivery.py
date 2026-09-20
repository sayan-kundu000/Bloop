"""
Audio Delivery & Storage Management Service
Handles temporary local audio storage, RFC 7233 HTTP Range streaming for player seeking,
attachment download delivery, user ownership authorization, and lifecycle cleanup.
"""

import os
import time
import uuid
from typing import Optional, Tuple, Union
from fastapi import Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.repositories.speech_generation import SpeechGenerationRepository
from backend.app.services.audio.exceptions import (
    AudioDeliveryException,
    AudioNotFoundException,
    GenerationAccessDeniedException,
    GenerationNotFoundException,
)


class AudioDeliveryService:
    """
    Manages audio file storage, ownership authorization, streaming, and download delivery.
    Ensures that temporary media assets are guarded against unauthorized access and path traversal.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or getattr(settings, "AUDIO_STORAGE_PATH", "backend/app/storage/audio")
        os.makedirs(self.storage_path, exist_ok=True)

    def store_temporary_audio(self, audio_bytes: bytes, extension: str = "mp3") -> str:
        """
        Writes raw audio bytes to server storage with a secure random UUID filename.
        Returns the basename of the persisted file.
        """
        clean_ext = extension.lstrip(".").lower() or "mp3"
        unique_id = uuid.uuid4().hex
        filename = f"{unique_id}.{clean_ext}"
        full_path = os.path.join(self.storage_path, filename)

        try:
            with open(full_path, "wb") as f:
                f.write(audio_bytes)
            logger.info(f"Persisted temporary audio file: {filename} ({len(audio_bytes)}B)")
            return filename
        except Exception as exc:
            logger.error(f"Failed to write audio file '{filename}': {exc}", exc_info=True)
            raise AudioDeliveryException(f"Failed to buffer audio to server storage: {exc}")

    def resolve_audio_file(
        self,
        identifier: Union[int, str],
        user_id: Optional[int],
        db: Session,
    ) -> Tuple[str, Optional[SpeechGeneration]]:
        """
        Authoritatively resolves and validates a requested audio generation asset:
        1. Queries generation record by ID or filename.
        2. Enforces ownership access control (HTTP 403 if non-owner).
        3. Sanitizes filename against path traversal (os.path.basename).
        4. Verifies physical file presence on server storage (HTTP 404 if missing).
        Returns tuple of (validated_file_path, SpeechGeneration).
        """
        repo = SpeechGenerationRepository(db)
        gen: Optional[SpeechGeneration] = None
        is_int_id = isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit())

        if is_int_id:
            gen = repo.get_by_id(int(identifier))
            if not gen:
                logger.warning(f"Generation record not found for ID {identifier}")
                raise GenerationNotFoundException(identifier=identifier)
        else:
            safe_query_filename = os.path.basename(str(identifier))
            gen = repo.get_by_filename(safe_query_filename)

        # Enforce strict user ownership access control (Prompt 13 §18)
        if gen is not None and gen.user_id is not None:
            if user_id is None or gen.user_id != user_id:
                logger.warning(
                    f"Access denied to generation {gen.id}: owner={gen.user_id}, requester={user_id or 'anonymous'}"
                )
                raise GenerationAccessDeniedException(generation_id=gen.id)

        # Resolve safe filename
        if gen is not None:
            safe_filename = os.path.basename(gen.audio_filename)
        else:
            safe_filename = os.path.basename(str(identifier))

        file_path = os.path.join(self.storage_path, safe_filename)

        if not os.path.exists(file_path):
            logger.warning(f"Audio file '{safe_filename}' is missing from storage")
            raise AudioNotFoundException(identifier=safe_filename)

        return file_path, gen

    def create_range_stream_response(
        self,
        file_path: str,
        range_header: Optional[str],
        content_type: str = "audio/mpeg",
    ) -> Response:
        """
        Constructs an HTTP response supporting RFC 7233 partial content range requests
        for seamless browser seeking, play, pause, and scrubber control.
        """
        file_size = os.path.getsize(file_path)

        if range_header:
            byte1, byte2 = 0, None
            try:
                clean_range = range_header.replace("bytes=", "").strip()
                parts = clean_range.split("-")
                if parts[0]:
                    byte1 = int(parts[0])
                if len(parts) > 1 and parts[1]:
                    byte2 = int(parts[1])
            except (ValueError, IndexError):
                byte1, byte2 = 0, None

            length = file_size - byte1 if byte2 is None else byte2 - byte1 + 1
            end_byte = byte2 or (file_size - 1)

            def send_bytes():
                with open(file_path, "rb") as f:
                    f.seek(byte1)
                    yield f.read(length)

            headers = {
                "Content-Range": f"bytes {byte1}-{end_byte}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
                "Content-Type": content_type,
            }
            return StreamingResponse(send_bytes(), status_code=206, headers=headers)

        return FileResponse(
            file_path,
            media_type=content_type,
            headers={"Accept-Ranges": "bytes"},
        )

    def create_download_response(
        self,
        file_path: str,
        generation_id: Optional[int],
        content_type: str = "audio/mpeg",
    ) -> FileResponse:
        """
        Returns a FileResponse configured with Content-Disposition: attachment,
        enforcing clean, deterministic filenames and preventing browser navigation disruption.
        """
        extension = file_path.split(".")[-1] if "." in file_path else "mp3"
        safe_id = generation_id if generation_id is not None else os.path.splitext(os.path.basename(file_path))[0]
        safe_download_name = f"bloop-speech-{safe_id}.{extension}"

        return FileResponse(
            file_path,
            media_type=content_type,
            filename=safe_download_name,
            headers={"Content-Disposition": f'attachment; filename="{safe_download_name}"'},
        )

    def cleanup_expired_audio(self, max_age_hours: int = 24) -> int:
        """
        Removes temporary audio files that exceed the retention window (Prompt 13 §23).
        Returns the number of pruned files.
        """
        pruned_count = 0
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        try:
            for entry in os.scandir(self.storage_path):
                if entry.is_file() and not entry.name.startswith("."):
                    stat = entry.stat()
                    if (now - stat.st_mtime) > max_age_seconds:
                        try:
                            os.remove(entry.path)
                            pruned_count += 1
                        except OSError as e:
                            logger.warning(f"Could not remove expired audio file '{entry.path}': {e}")
        except Exception as exc:
            logger.error(f"Error executing audio directory cleanup: {exc}")

        if pruned_count > 0:
            logger.info(f"Pruned {pruned_count} expired temporary audio files from {self.storage_path}")
        return pruned_count

    def delete_audio_file(self, filename: str) -> bool:
        """Safely removes a specific audio file from storage."""
        safe_name = os.path.basename(filename)
        path = os.path.join(self.storage_path, safe_name)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except OSError as exc:
                logger.warning(f"Failed to delete audio file '{safe_name}': {exc}")
        return False
