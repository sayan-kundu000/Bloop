"""
Bloop Hybrid Intelligence & Benchmarking Exceptions
Defines structured domain-level errors for hybrid analysis, fusion,
multi-category benchmarking, speech recommendations, and capability validation.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import BloopException


class BenchmarkInvalidException(BloopException):
    """Raised when benchmark parameters, category, or configuration are invalid."""

    def __init__(self, message: str = "Benchmark configuration is invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BENCHMARK_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class BenchmarkDatasetInvalidException(BloopException):
    """Raised when benchmark dataset is missing, corrupted, or incompatible."""

    def __init__(self, message: str = "Benchmark dataset is invalid or unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BENCHMARK_DATASET_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class BenchmarkResourceLimitException(BloopException):
    """Raised when requested benchmark exceeds bounded resource limits (samples, qubits, shots)."""

    def __init__(self, message: str = "Benchmark request exceeds computational limits.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BENCHMARK_RESOURCE_LIMIT",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class BenchmarkExecutionFailedException(BloopException):
    """Raised when benchmark evaluation fails during training or inference."""

    def __init__(self, message: str = "Benchmark evaluation failed during execution.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BENCHMARK_EXECUTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class BenchmarkMetricFailedException(BloopException):
    """Raised when metric calculation fails or produces invalid statistical values."""

    def __init__(self, message: str = "Benchmark metric calculation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BENCHMARK_METRIC_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class HybridAnalysisFailedException(BloopException):
    """Raised when hybrid analysis execution fails across classical or quantum pipelines."""

    def __init__(self, message: str = "Hybrid intelligence analysis failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="HYBRID_ANALYSIS_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class HybridFusionFailedException(BloopException):
    """Raised when classical and quantum representations cannot be mathematically fused."""

    def __init__(self, message: str = "Hybrid intelligence fusion failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="HYBRID_FUSION_FAILED",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class RecommendationFailedException(BloopException):
    """Raised when deriving acoustic speech parameters fails."""

    def __init__(self, message: str = "Speech recommendation generation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RECOMMENDATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class RecommendationUnsupportedException(BloopException):
    """Raised when the requested recommendation parameters or modality are unsupported."""

    def __init__(self, message: str = "Requested recommendation parameters are unsupported.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RECOMMENDATION_UNSUPPORTED",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class SpeechRecommendationInvalidException(BloopException):
    """Raised when recommendation values violate acoustic safety bounds."""

    def __init__(self, message: str = "Speech recommendation values are out of bounds.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SPEECH_RECOMMENDATION_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class SpeechCapabilityMismatchException(BloopException):
    """Raised when recommended speech settings are incompatible with dynamic voice capabilities."""

    def __init__(self, message: str = "Recommended settings do not match voice capabilities.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SPEECH_CAPABILITY_MISMATCH",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )
