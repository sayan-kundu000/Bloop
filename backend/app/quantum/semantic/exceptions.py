"""
Bloop Quantum Semantic Intelligence Exceptions
Defines domain-specific errors for the quantum semantic intelligence,
similarity analysis, dimensionality reduction, quantum kernel, and classical baseline pipeline.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import BloopException


class SemanticAnalysisFailedException(BloopException):
    """Raised when overall semantic similarity analysis fails."""

    def __init__(self, message: str = "Quantum semantic similarity analysis failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_ANALYSIS_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticInputInvalidException(BloopException):
    """Raised when text inputs for semantic analysis are empty, whitespace, or invalid."""

    def __init__(self, message: str = "Semantic input text is invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_INPUT_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class SemanticFeatureExtractionFailedException(BloopException):
    """Raised when classical semantic feature representation extraction fails."""

    def __init__(self, message: str = "Semantic feature extraction failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_FEATURE_EXTRACTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticReductionFailedException(BloopException):
    """Raised when dimensionality reduction (TruncatedSVD) fails."""

    def __init__(self, message: str = "Semantic dimensionality reduction failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_REDUCTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticEncodingFailedException(BloopException):
    """Raised when feature angle encoding or mapping fails."""

    def __init__(self, message: str = "Semantic quantum encoding failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_ENCODING_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticKernelFailedException(BloopException):
    """Raised when quantum kernel evaluation or transition fidelity circuit fails."""

    def __init__(self, message: str = "Quantum semantic kernel evaluation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_KERNEL_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticSimilarityFailedException(BloopException):
    """Raised when classical or hybrid similarity computation encounters an error."""

    def __init__(self, message: str = "Semantic similarity computation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_SIMILARITY_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticBenchmarkFailedException(BloopException):
    """Raised when semantic benchmark execution or evaluation fails."""

    def __init__(self, message: str = "Semantic benchmark execution failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_BENCHMARK_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class SemanticDatasetInvalidException(BloopException):
    """Raised when the semantic benchmark dataset is malformed or invalid."""

    def __init__(self, message: str = "Semantic benchmark dataset is invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_DATASET_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class SemanticResourceLimitException(BloopException):
    """Raised when requested semantic operations exceed defined computational or safety limits."""

    def __init__(self, message: str = "Semantic resource limits exceeded.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEMANTIC_RESOURCE_LIMIT",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )
