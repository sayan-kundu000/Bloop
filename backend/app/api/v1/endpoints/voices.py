from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.voice import VoiceResponse, VoiceCreate
from backend.app.services.voice_service import VoiceService

router = APIRouter()


@router.get("", response_model=ApiResponse[List[VoiceResponse]])
def get_voices(
    language: Optional[str] = Query(None, description="Filter by language code (e.g. en-US, es-ES)"),
    language_code: Optional[str] = Query(None, description="Alias for language filter"),
    gender: Optional[str] = Query(None, description="Filter by gender (female, male, neutral, all)"),
    search: Optional[str] = Query(None, description="Search voices by name, accent, or description"),
    db: Session = Depends(get_db),
):
    """
    Retrieve dynamically available voices.
    Supports filtering by language locale (via ?language= or ?language_code=), gender, and keyword search.
    Returns an empty list if no voices are currently configured.
    """
    service = VoiceService(db)
    target_lang = language or language_code
    voices = service.get_voices(language_code=target_lang, gender=gender, search=search, active_only=True)

    result = []
    for v in voices:
        resp = VoiceResponse.model_validate(v)
        resp.supported_languages = service.get_supported_languages(v)
        result.append(resp)

    return ApiResponse(
        success=True,
        data=result,
        message="Voices retrieved successfully",
    )


@router.get("/{voice_id}", response_model=ApiResponse[VoiceResponse])
def get_voice(voice_id: str, db: Session = Depends(get_db)):
    """
    Retrieve metadata for a specific voice by its voice_id.
    """
    service = VoiceService(db)
    voice = service.get_voice_by_id(voice_id)
    if not voice or not voice.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "VOICE_NOT_FOUND", "message": f"Voice '{voice_id}' not found or inactive"},
        )
    resp = VoiceResponse.model_validate(voice)
    resp.supported_languages = service.get_supported_languages(voice)
    return ApiResponse(
        success=True,
        data=resp,
        message="Voice retrieved successfully",
    )



@router.post("", response_model=ApiResponse[VoiceResponse])
def register_voice(
    voice_in: VoiceCreate,
    db: Session = Depends(get_db),
):
    """
    Dynamically register a user-provided voice (e.g. an ElevenLabs voice ID).
    Enforces dynamic voice architecture without code modifications.
    """
    service = VoiceService(db)
    try:
        voice = service.register_user_voice(voice_in)
        return ApiResponse(
            success=True,
            data=VoiceResponse.model_validate(voice),
            message=f"Voice '{voice.name}' registered successfully.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VOICE_REGISTRATION_FAILED", "message": str(e)},
        )


@router.post("/reload-config", response_model=ApiResponse[dict])
def reload_voices_from_config(db: Session = Depends(get_db)):
    """
    Reload custom voices from backend/voices_config.json.
    """
    service = VoiceService(db)
    count = service.import_voices_from_config()
    return ApiResponse(
        success=True,
        data={"imported_count": count},
        message=f"Imported {count} custom voices from configuration file.",
    )
