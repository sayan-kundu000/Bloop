"""
Bloop API Dependencies Module
Re-exports dependencies for clean imports across routes and tests.
"""

from backend.app.api.deps import (
    get_auth_service,
    get_current_active_superuser,
    get_current_user,
    get_http_client,
    get_optional_current_user,
    get_quantum_service,
    get_settings,
    get_speech_service,
    get_voice_service,
    oauth2_scheme,
)
from backend.app.db.dependencies import get_db

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
