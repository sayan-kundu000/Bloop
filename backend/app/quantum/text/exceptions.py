"""
Bloop Quantum Text Intelligence Exceptions
Defines domain-specific errors for the quantum text processing,
feature engineering, circuit encoding, and hybrid classification pipeline.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import BloopException, ErrorCode, ValidationException


class QuantumTextInvalidException(ValidationException):
    """Raised when text input fails validation rules (empty, whitespace, excessive length)."""

    def __init__(self, message: str = "Invalid text for quantum analysis.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_QUANTUM_REQUEST,
            details=details,
        )


class TextFeatureExtractionFailedException(BloopException):
    """Raised when classical TF-IDF or lexical vectorization fails."""

    def __init__(self, message: str = "Classical text feature extraction failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="TEXT_FEATURE_EXTRACTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class FeatureDimensionTooLargeException(ValidationException):
    """Raised when the extracted feature dimensionality exceeds quantum resource boundaries."""

    def __init__(self, message: str = "Feature dimension exceeds allowable quantum capacity.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FEATURE_DIMENSION_TOO_LARGE",
            details=details,
        )


class FeatureReductionFailedException(BloopException):
    """Raised when dimensionality reduction (e.g. TruncatedSVD) encounters numerical singularity or fails."""

    def __init__(self, message: str = "Feature dimensionality reduction failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FEATURE_REDUCTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class FeatureEncodingFailedException(BloopException):
    """Raised when numerical values cannot be mapped to quantum rotation angles (NaN, Inf, empty)."""

    def __init__(self, message: str = "Quantum feature angle encoding failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FEATURE_ENCODING_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ClassifierUnavailableException(BloopException):
    """Raised when requested quantum or classical classifier model strategy is unavailable."""

    def __init__(self, message: str = "Requested classifier strategy is unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CLASSIFIER_UNAVAILABLE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class QuantumClassificationFailedException(BloopException):
    """Raised when quantum circuit simulation or decision layer inference fails."""

    def __init__(self, message: str = "Quantum classification execution failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="QUANTUM_CLASSIFICATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class DatasetInvalidException(ValidationException):
    """Raised when training/evaluation corpus contains invalid, mismatched, or insufficient samples."""

    def __init__(self, message: str = "Evaluation dataset is invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATASET_INVALID",
            details=details,
        )


class ModelTrainingFailedException(BloopException):
    """Raised when model fitting on training split fails."""

    def __init__(self, message: str = "Model training failed on training split.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_TRAINING_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ModelPredictionFailedException(BloopException):
    """Raised when model inference on test split or input text fails."""

    def __init__(self, message: str = "Model prediction failed during inference.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_PREDICTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )
