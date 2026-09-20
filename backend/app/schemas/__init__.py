"""
Bloop Pydantic Schemas Subsystem
Exports all domain request/response contracts for FastAPI validation and serialization.
"""

from backend.app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    Token,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from backend.app.schemas.common import (
    ApiResponse,
    ErrorDetail,
    PaginatedResponse,
    PaginationMeta,
)
from backend.app.schemas.favorite import (
    FavoriteCreate,
    FavoriteDeleteResponse,
    FavoriteResponse,
)
from backend.app.schemas.history import (
    GenerationResponse,
    HistoryItemResponse,
    HistoryQueryFilter,
)
from backend.app.schemas.language import (
    LanguageBase,
    LanguageCreate,
    LanguageResponse,
    LanguageUpdate,
)
from backend.app.schemas.capability import (
    CapabilityCheckResponse,
    ProviderCapabilityResponse,
    VoiceLanguageCapabilityResponse,
)

from backend.app.schemas.quantum import (
    BenchmarkRequest,
    GateOperation,
    MetricComparison,
    QuantumBenchmarkResponse,
    QuantumCircuitRequest,
    QuantumCircuitResponse,
    QuantumEmotionRequest,
    QuantumEmotionResponse,
    QuantumSemanticRequest,
    QuantumSemanticResponse,
    QuantumTextRequest,
    QuantumTextResponse,
)
from backend.app.schemas.tts import (
    AudioVideoReference,
    QuantumDecisionDetails,
    QuantumResonanceMetrics,
    TTSRequest,
    TTSResponse,
    TextAnalyzeRequest,
    TextStatsResponse,
)
from backend.app.schemas.user import (
    UserBase,
    UserDetailResponse,
    UserPreferenceBase,
    UserPreferenceResponse,
    UserPreferenceUpdate,
    UserProfileUpdateRequest,
    UserResponse,
    UserUpdate,
)
from backend.app.schemas.voice import (
    VoiceBase,
    VoiceCreate,
    VoiceResponse,
    VoiceUpdate,
)

__all__ = [
    # Common
    "ApiResponse",
    "ErrorDetail",
    "PaginationMeta",
    "PaginatedResponse",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "Token",
    "LogoutResponse",
    "UserCreate",
    "UserLogin",
    # User
    "UserBase",
    "UserProfileUpdateRequest",
    "UserUpdate",
    "UserResponse",
    "UserDetailResponse",
    "UserPreferenceBase",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",
    # Language
    "LanguageBase",
    "LanguageCreate",
    "LanguageUpdate",
    "LanguageResponse",
    # Capability
    "ProviderCapabilityResponse",
    "VoiceLanguageCapabilityResponse",
    "CapabilityCheckResponse",
    # Voice
    "VoiceBase",
    "VoiceCreate",
    "VoiceUpdate",
    "VoiceResponse",
    # TTS
    "TTSRequest",
    "TTSResponse",
    "TextAnalyzeRequest",
    "TextStatsResponse",
    "AudioVideoReference",
    "QuantumDecisionDetails",
    "QuantumResonanceMetrics",
    # History
    "HistoryItemResponse",
    "GenerationResponse",
    "HistoryQueryFilter",
    # Favorite
    "FavoriteCreate",
    "FavoriteResponse",
    "FavoriteDeleteResponse",
    # Quantum
    "QuantumTextRequest",
    "QuantumTextResponse",
    "QuantumEmotionRequest",
    "QuantumEmotionResponse",
    "QuantumSemanticRequest",
    "QuantumSemanticResponse",
    "GateOperation",
    "QuantumCircuitRequest",
    "QuantumCircuitResponse",
    "BenchmarkRequest",
    "MetricComparison",
    "QuantumBenchmarkResponse",
]
