"""
Bloop Text-to-Speech (TTS) Endpoints
Provides text-to-speech synthesis, real-time text analysis, RFC 7233 audio range streaming,
attachment download delivery, and user ownership access control.
Enforces authentication boundaries and provider isolation.
"""

from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_optional_current_user
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    BloopException,
    ErrorCode,
    GenerationAccessDeniedException,
    ProviderException,
    ResourceNotFoundException,
    ValidationException,
)
from backend.app.core.rate_limit import rate_limit
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.tts import (
    TextAnalyzeRequest,
    TextStatsResponse,
    TTSRequest,
    TTSResponse,
)
from backend.app.services.audio import AudioDeliveryService
from backend.app.services.speech import SpeechService

router = APIRouter()
audio_delivery = AudioDeliveryService()


@router.post(
    "",
    response_model=ApiResponse[TTSResponse],
    dependencies=[Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_TTS))],
)
async def generate_speech(
    request: TTSRequest,
    request_http: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Core Text-to-Speech Generation Endpoint (Protected).
    Enforces authentication, resolves dynamic voices, validates text boundaries,
    executes provider synthesis (ElevenLabs or simulation fallback),
    persists generation metadata with user ownership, and returns streamable audio URLs.
    """
    speech_service = SpeechService(db)
    request_id = getattr(request_http.state, "request_id", None)

    try:
        response_data = await speech_service.generate_speech(
            request,
            user_id=current_user.id,
            request_id=request_id,
        )
        return ApiResponse(
            success=True,
            data=response_data,
            message="Audio generated successfully.",
        )
    except BloopException:
        raise
    except ValueError as e:
        raise ValidationException(str(e), details={"error": str(e)})
    except PermissionError as e:
        raise ProviderException(
            provider="elevenlabs",
            message=f"Provider authentication failed: {e}",
            code=ErrorCode.TTS_PROVIDER_UNAVAILABLE,
        )
    except LookupError as e:
        raise ResourceNotFoundException(resource="Voice", identifier=request.voice_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": ErrorCode.TTS_GENERATION_FAILED, "message": str(e)},
        )


@router.post("/analyze", response_model=ApiResponse[TextStatsResponse])
def analyze_text(
    payload: TextAnalyzeRequest,
    db: Session = Depends(get_db),
):
    """
    Real-time text analysis endpoint for frontend character, word, and duration estimates.
    Available to authenticated and unauthenticated callers.
    """
    speech_service = SpeechService(db)
    stats = speech_service.analyze_text(payload.text)
    return ApiResponse(success=True, data=stats, message="Text analyzed successfully.")


@router.get(
    "/audio/{identifier}",
    dependencies=[Depends(rate_limit(requests_per_minute=60))],
)
def stream_audio(
    identifier: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """
    Stream generated audio with HTTP Range support (RFC 7233) for seeking, play, and pause.
    Enforces authentication and user ownership:
    - Returns HTTP 401 if unauthenticated.
    - Returns HTTP 403 if accessed by a non-owner.
    Supports either filename (uuid.mp3) or generation_id.
    """
    file_path, gen = audio_delivery.resolve_audio_file(identifier, user_id=current_user.id, db=db)

    content_type = "audio/mpeg"
    if gen and gen.audio_format == "wav":
        content_type = "audio/wav"
    elif file_path.endswith(".wav"):
        content_type = "audio/wav"

    range_header = request.headers.get("range")
    return audio_delivery.create_range_stream_response(
        file_path=file_path,
        range_header=range_header,
        content_type=content_type,
    )


@router.get(
    "/download/{identifier}",
    dependencies=[Depends(rate_limit(requests_per_minute=60))],
)
def download_audio(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """
    Direct audio download endpoint returning Content-Disposition: attachment.
    Enforces authentication and user ownership:
    - Returns HTTP 401 if unauthenticated.
    - Returns HTTP 403 if accessed by a non-owner.
    Supports either filename or generation_id.
    """
    file_path, gen = audio_delivery.resolve_audio_file(identifier, user_id=current_user.id, db=db)

    content_type = "audio/mpeg"
    generation_id = gen.id if gen else None
    if gen and gen.audio_format == "wav":
        content_type = "audio/wav"
    elif file_path.endswith(".wav"):
        content_type = "audio/wav"

    return audio_delivery.create_download_response(
        file_path=file_path,
        generation_id=generation_id,
        content_type=content_type,
    )


@router.get(
    "/{generation_id}/audio",
    dependencies=[Depends(rate_limit(requests_per_minute=60))],
)
def stream_generation_audio(
    generation_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """
    Direct generation ID audio stream route (Prompt 13 §15 & Prompt 14 §37).
    Enforces authentication and generation ownership.
    """
    return stream_audio(identifier=str(generation_id), request=request, current_user=current_user, db=db)


@router.get(
    "/{generation_id}/download",
    dependencies=[Depends(rate_limit(requests_per_minute=60))],
)
def download_generation_audio(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """
    Direct generation ID download route (Prompt 13 §15 & Prompt 14 §37).
    Enforces authentication and generation ownership.
    """
    return download_audio(identifier=str(generation_id), current_user=current_user, db=db)
