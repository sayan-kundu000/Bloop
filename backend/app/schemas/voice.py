from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class VoiceBase(BaseModel):
    voice_id: str = Field(..., description="Unique application voice identifier")
    name: str = Field(..., description="Display name for the voice")
    language_code: str = Field(..., description="Primary language locale code, e.g. en-US")
    gender: str = Field("unspecified", description="Gender descriptor: female, male, neutral, unspecified")
    accent: Optional[str] = Field(None, description="Regional accent or dialect descriptor")
    description: Optional[str] = Field(None, description="Descriptive summary of voice characteristics")
    provider: str = Field("dynamic", description="Provider identifier: elevenlabs, dynamic, simulation")
    preview_url: Optional[str] = Field(None, description="Sample audio preview URL")
    is_active: bool = Field(True, description="Whether this voice is active and selectable")
    is_user_configured: bool = Field(False, description="Whether this voice was registered dynamically")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Extensible voice attributes")


class VoiceCreate(VoiceBase):
    provider_voice_id: Optional[str] = Field(
        None,
        description="Optional internal provider voice ID (e.g. ElevenLabs ID); isolates vendor ID from public API",
    )


class VoiceUpdate(BaseModel):
    name: Optional[str] = None
    language_code: Optional[str] = None
    gender: Optional[str] = None
    accent: Optional[str] = None
    description: Optional[str] = None
    preview_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_user_configured: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class VoiceResponse(VoiceBase):
    id: int
    supported_languages: List[str] = Field(
        default_factory=list,
        description="All language codes supported by this voice (combines primary and M2M capabilities)",
    )

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "__table__"):
            return {
                "id": getattr(data, "id", None),
                "voice_id": getattr(data, "voice_id", None),
                "name": getattr(data, "name", None),
                "language_code": getattr(data, "language_code", None),
                "gender": getattr(data, "gender", "unspecified"),
                "accent": getattr(data, "accent", None),
                "description": getattr(data, "description", None),
                "provider": getattr(data, "provider", "dynamic"),
                "preview_url": getattr(data, "preview_url", None),
                "is_active": getattr(data, "is_active", True),
                "is_user_configured": getattr(data, "is_user_configured", False),
                "metadata": getattr(data, "metadata_json", None),
                "supported_languages": getattr(data, "supported_languages", []),
            }
        return data

    class Config:
        from_attributes = True


