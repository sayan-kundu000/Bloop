"""
Bloop TTS Capability Schemas
Pydantic contracts for provider and voice-language capabilities.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProviderCapabilityResponse(BaseModel):
    provider: str = Field(..., description="TTS provider identifier (e.g. elevenlabs, simulation)")
    language_code: str = Field(..., description="Language code")
    provider_language_code: Optional[str] = Field(None, description="Mapped provider-specific code")
    supported: bool = Field(..., description="Whether provider supports this language")
    enabled: bool = Field(..., description="Whether Bloop enables this provider language")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class VoiceLanguageCapabilityResponse(BaseModel):
    voice_id: int
    language_code: str
    supported: bool
    enabled: bool
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CapabilityCheckResponse(BaseModel):
    voice_id: str
    language_code: str
    is_compatible: bool
    supported_languages: List[str] = Field(default_factory=list)
