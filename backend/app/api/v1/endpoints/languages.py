from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.language import LanguageResponse
from backend.app.services.language_service import LanguageService

router = APIRouter()


@router.get("", response_model=ApiResponse[List[LanguageResponse]])
def get_languages(db: Session = Depends(get_db)):
    """
    Retrieve all available application languages.
    Returns an empty list if no languages are currently configured.
    """
    service = LanguageService(db)
    languages = service.get_languages(active_only=True)
    return ApiResponse(
        success=True,
        data=[LanguageResponse.model_validate(l) for l in languages],
        message="Languages retrieved successfully",
    )


@router.get("/{code}", response_model=ApiResponse[LanguageResponse])
def get_language(code: str, db: Session = Depends(get_db)):
    """
    Retrieve metadata for a specific language by its code.
    """
    service = LanguageService(db)
    lang = service.get_language(code)
    if not lang or not lang.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "LANGUAGE_NOT_FOUND", "message": f"Language '{code}' not found or inactive"},
        )
    return ApiResponse(
        success=True,
        data=LanguageResponse.model_validate(lang),
        message="Language retrieved successfully",
    )

