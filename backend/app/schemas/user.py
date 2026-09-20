"""
Bloop User Domain Schemas
Defines request and response schemas for user identity, profile modifications, and UI preferences.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full display name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Account password (min 6 characters)")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Account email")
    password: str = Field(..., description="Account password")


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="Updated full display name (safe profile modification)")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="Updated full display name")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="Updated account password")



class UserPreferenceBase(BaseModel):
    theme: Optional[str] = Field("dark", pattern="^(dark|light|system)$", description="UI theme preference")
    audio_speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Default playback speed multiplier")
    auto_play: Optional[bool] = Field(True, description="Automatically play synthesized speech")
    default_language_code: Optional[str] = Field(None, max_length=10, description="Default language code (e.g. en-US)")
    default_voice_id: Optional[str] = Field(None, max_length=100, description="Default voice identifier")


class UserPreferenceUpdate(BaseModel):
    theme: Optional[str] = Field(None, pattern="^(dark|light|system)$", description="Updated UI theme")
    audio_speed: Optional[float] = Field(None, ge=0.5, le=2.0, description="Updated playback speed")
    auto_play: Optional[bool] = Field(None, description="Updated auto-play flag")
    default_language_code: Optional[str] = Field(None, max_length=10, description="Updated default language")
    default_voice_id: Optional[str] = Field(None, max_length=100, description="Updated default voice")


class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    theme: str
    audio_speed: float
    auto_play: bool
    default_language_code: Optional[str] = None
    default_voice_id: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    preference: Optional[UserPreferenceResponse] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
