"""
API Dependency Subsystem
Encapsulates reusable FastAPI parameter and security dependencies.
"""

from backend.app.api.dependencies import (
    get_auth_service,
    get_current_active_superuser,
    get_current_user,
    get_db,
    get_http_client,
    get_optional_current_user,
    get_quantum_service,
    get_settings,
    get_speech_service,
    get_voice_service,
    oauth2_scheme,
)

__all__ = [
    "get_db",
    "get_settings",
    "get_current_user",
    "get_optional_current_user",
    "get_current_active_superuser",
    "get_http_client",
    "get_auth_service",
    "get_voice_service",
    "get_speech_service",
    "get_quantum_service",
    "oauth2_scheme",
]
