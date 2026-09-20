"""
Bloop Centralized Core Configuration Module
Defines typed, validated, and environment-aware settings for the Bloop platform.
Adheres strictly to Twelve-Factor principles and enforces safety boundaries across
development, test, and production runtime profiles.
"""

import os
from functools import lru_cache
from typing import Any, List, Literal, Union
from urllib.parse import urlsplit, urlunsplit
from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration settings with environment validation."""

    # --------------------------------------------------------------------------
    # 1. Application Settings
    # --------------------------------------------------------------------------
    APP_NAME: str = "Bloop"
    APP_ENV: Literal["development", "test", "production"] = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"),
        description="Active runtime environment profile.",
    )
    APP_DEBUG: bool = Field(
        default=True,
        validation_alias=AliasChoices("APP_DEBUG", "DEBUG"),
        description="Enable debug mode and verbose tracebacks.",
    )
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        validation_alias=AliasChoices("API_V1_PREFIX", "API_V1_STR"),
        description="Prefix namespace for v1 REST endpoints.",
    )
    PORT: int = 8000

    # --------------------------------------------------------------------------
    # 2. Relational Database Settings
    # --------------------------------------------------------------------------
    DATABASE_URL: str = Field(
        default="sqlite:///./bloop.db",
        description="Database connection URI (PostgreSQL in production, SQLite fallback in local dev).",
    )

    # --------------------------------------------------------------------------
    # 3. Authentication & JWT Security Settings
    # --------------------------------------------------------------------------
    JWT_SECRET_KEY: str = Field(
        default="dev-insecure-secret-key-32characters-minimum-for-testing",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY"),
        description="HMAC secret key used for signing JWT access tokens.",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # --------------------------------------------------------------------------
    # 4. Text-to-Speech (ElevenLabs) Provider Settings
    # --------------------------------------------------------------------------
    ELEVENLABS_API_KEY: str = Field(
        default="",
        description="ElevenLabs API key (empty by default to use offline simulation).",
    )
    ELEVENLABS_API_BASE: str = "https://api.elevenlabs.io/v1"
    ELEVENLABS_CONNECT_TIMEOUT_SECONDS: float = Field(
        default=5.0,
        description="Timeout in seconds for establishing connection to ElevenLabs API.",
    )
    ELEVENLABS_READ_TIMEOUT_SECONDS: float = Field(
        default=30.0,
        description="Timeout in seconds for reading speech audio response from ElevenLabs API.",
    )
    ELEVENLABS_MAX_RETRIES: int = Field(
        default=2,
        description="Maximum retry attempts on transient network or 5xx server errors.",
    )
    ELEVENLABS_DEFAULT_MODEL_ID: str = Field(
        default="eleven_multilingual_v2",
        description="Default ElevenLabs synthesis model ID.",
    )

    # --------------------------------------------------------------------------
    # 5. Cross-Origin Resource Sharing (CORS) Settings
    # --------------------------------------------------------------------------
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "https://bloop.vercel.app",
        ],
        validation_alias=AliasChoices("CORS_ORIGINS", "BACKEND_CORS_ORIGINS"),
        description="Allowed origin URLs for browser client CORS negotiations.",
    )

    # --------------------------------------------------------------------------
    # 6. Rate Limiting Settings
    # --------------------------------------------------------------------------
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE_TTS: int = 10
    RATE_LIMIT_PER_MINUTE_QUANTUM: int = 15
    RATE_LIMIT_PER_MINUTE_AUTH: int = 5

    # --------------------------------------------------------------------------
    # 7. Local Audio Storage & Text Constraints
    # --------------------------------------------------------------------------
    AUDIO_STORAGE_PATH: str = "backend/app/storage/audio"
    MIN_TEXT_CHARACTERS: int = Field(
        default=1,
        validation_alias=AliasChoices("MIN_TEXT_CHARACTERS", "MIN_TEXT_LENGTH"),
        description="Minimum allowed text length for speech synthesis.",
    )
    MAX_TEXT_CHARACTERS: int = Field(
        default=2500,
        validation_alias=AliasChoices("MAX_TEXT_CHARACTERS", "MAX_TEXT_LENGTH"),
        description="Maximum allowed character limit for speech synthesis.",
    )
    MIN_TEXT_LENGTH: int = 1
    MAX_TEXT_LENGTH: int = 2500

    # --------------------------------------------------------------------------
    # 8. Quantum Intelligence Settings
    # --------------------------------------------------------------------------
    QUANTUM_ENABLED: bool = True
    QUANTUM_SIMULATOR_SHOTS: int = 1024
    QUANTUM_MAX_QUBITS: int = 8
    QUANTUM_MAX_SHOTS: int = 8192
    QUANTUM_MAX_EXECUTION_TIME: int = 30  # seconds

    # --------------------------------------------------------------------------
    # 9. Logging Settings
    # --------------------------------------------------------------------------
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # --------------------------------------------------------------------------
    # Pydantic Settings Configuration
    # --------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=("backend/.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --------------------------------------------------------------------------
    # Normalizers and Field Validators
    # --------------------------------------------------------------------------
    @field_validator("APP_ENV", mode="before")
    @classmethod
    def normalize_app_env(cls, v: Any) -> str:
        """Normalizes environment name to canonical profile: development, test, or production."""
        if isinstance(v, str):
            clean = v.strip().lower()
            if clean in ("testing", "test"):
                return "test"
            if clean in ("prod", "production"):
                return "production"
            if clean in ("dev", "development", "local"):
                return "development"
            return clean
        return v

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def normalize_log_level(cls, v: Any) -> str:
        """Normalizes log level string to uppercase."""
        if isinstance(v, str):
            return v.strip().upper()
        return v

    # --------------------------------------------------------------------------
    # Profile & Security Safeguard Model Validator
    # --------------------------------------------------------------------------
    @model_validator(mode="after")
    def validate_environment_guards(self) -> "Settings":
        """
        Enforces strict fail-fast security constraints based on the active runtime profile.
        """
        # Production profile safeguards
        if self.APP_ENV == "production":
            if self.APP_DEBUG:
                raise ValueError(
                    "Production safety violation: APP_DEBUG must be False in production mode. "
                    "Debug mode cannot run in production."
                )

            insecure_key_indicators = {
                "dev-insecure-secret-key-32characters-minimum-for-testing",
                "bloop-development-insecure-secret-key-for-local-testing-only-32chars",
                "secret",
                "password",
                "changeme",
                "123456",
                "admin",
            }
            clean_secret = self.JWT_SECRET_KEY.strip()
            if not clean_secret or clean_secret in insecure_key_indicators or len(clean_secret) < 32:
                raise ValueError(
                    "Production safety violation: JWT_SECRET_KEY must be a cryptographically "
                    "secure secret (minimum 32 characters) and cannot be a default development placeholder."
                )

            if not self.DATABASE_URL or self.DATABASE_URL.startswith("sqlite"):
                raise ValueError(
                    "Production safety violation: Production requires a persistent PostgreSQL DATABASE_URL. "
                    "SQLite fallback is strictly prohibited in production."
                )

            if "*" in self.cors_origins:
                raise ValueError(
                    "Production safety violation: Wildcard CORS ('*') is prohibited in production mode. "
                    "Explicitly define trusted client domains."
                )

        # Test profile safeguards (prevent destructive operations against production database)
        if self.APP_ENV == "test":
            prod_db_indicators = ["render.com", "dpg-", "prod-db", "production-db"]
            if any(ind in self.DATABASE_URL.lower() for ind in prod_db_indicators):
                raise ValueError(
                    "Test isolation violation: Automated tests detected a production database URL. "
                    "Tests must use an isolated test database (e.g. sqlite:///./test_bloop.db)."
                )

        return self

    # --------------------------------------------------------------------------
    # Backward-Compatibility Property Accessors
    # --------------------------------------------------------------------------
    @property
    def ENVIRONMENT(self) -> str:
        """Legacy alias for APP_ENV."""
        return self.APP_ENV

    @property
    def DEBUG(self) -> bool:
        """Legacy alias for APP_DEBUG."""
        return self.APP_DEBUG

    @property
    def API_V1_STR(self) -> str:
        """Legacy alias for API_V1_PREFIX."""
        return self.API_V1_PREFIX

    @property
    def SECRET_KEY(self) -> str:
        """Legacy alias for JWT_SECRET_KEY."""
        return self.JWT_SECRET_KEY

    @property
    def BACKEND_CORS_ORIGINS(self) -> Union[List[str], str]:
        """Legacy alias for CORS_ORIGINS."""
        return self.CORS_ORIGINS

    @property
    def cors_origins(self) -> List[str]:
        """Parses CORS_ORIGINS into a clean List[str]."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return list(self.CORS_ORIGINS)

    # --------------------------------------------------------------------------
    # Safe Masking for Representation and Logging
    # --------------------------------------------------------------------------
    def get_masked_database_url(self) -> str:
        """Returns database URL with credentials safely masked."""
        if not self.DATABASE_URL:
            return "<UNSET>"
        try:
            parsed = urlsplit(self.DATABASE_URL)
            if parsed.password:
                netloc = f"{parsed.username or ''}:***@{parsed.hostname or ''}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
            return self.DATABASE_URL
        except Exception:
            return "***MASKED_URL***"

    def __repr__(self) -> str:
        masked_db = self.get_masked_database_url()
        masked_jwt = "***MASKED***" if self.JWT_SECRET_KEY else "<UNSET>"
        masked_eleven = "***MASKED***" if self.ELEVENLABS_API_KEY else "<UNSET>"
        return (
            f"Settings("
            f"APP_NAME={self.APP_NAME!r}, "
            f"APP_ENV={self.APP_ENV!r}, "
            f"APP_DEBUG={self.APP_DEBUG!r}, "
            f"APP_VERSION={self.APP_VERSION!r}, "
            f"API_V1_PREFIX={self.API_V1_PREFIX!r}, "
            f"DATABASE_URL={masked_db!r}, "
            f"JWT_SECRET_KEY={masked_jwt!r}, "
            f"ELEVENLABS_API_KEY={masked_eleven!r}, "
            f"LOG_LEVEL={self.LOG_LEVEL!r}"
            f")"
        )

    def __str__(self) -> str:
        return self.__repr__()


@lru_cache()
def get_settings() -> Settings:
    """Returns cached Settings singleton instance."""
    return Settings()


# Primary global singleton
settings: Settings = get_settings()

# Ensure local audio storage directory exists
try:
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
except Exception:
    pass
