from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator


class LanguageBase(BaseModel):
    code: str = Field(..., description="ISO 639-1 / BCP-47 language tag (e.g. en-US, es-ES)")
    name: str = Field(..., description="English display name of the language")
    native_name: Optional[str] = Field(None, description="Native script display name")
    direction: str = Field("ltr", description="Text layout direction: 'ltr' or 'rtl'")
    is_active: bool = Field(True, description="Whether this language is currently active in Bloop")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Extensible locale and script metadata")


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = None
    native_name: Optional[str] = None
    direction: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class LanguageResponse(LanguageBase):
    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "__table__"):
            return {
                "code": getattr(data, "code", None),
                "name": getattr(data, "name", None),
                "native_name": getattr(data, "native_name", None),
                "direction": getattr(data, "direction", "ltr"),
                "is_active": getattr(data, "is_active", True),
                "metadata": getattr(data, "metadata_json", None),
            }
        return data

    class Config:
        from_attributes = True


