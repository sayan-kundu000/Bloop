"""
Bloop Quantum Emotion Intelligence Exceptions
Defines domain-specific errors for the quantum emotion intelligence,
affective feature engineering, hybrid QNN, and speech recommendation pipeline.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import BloopException, ErrorCode, ValidationException


class EmotionAnalysisFailedException(BloopException):
    """Raised when overall emotion analysis fails."""

    def __init__(self, message: str = "Quantum emotion analysis failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_ANALYSIS_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class EmotionFeatureExtractionFailedException(BloopException):
    """Raised when lexical or statistical affective feature extraction fails."""

    def __init__(self, message: str = "Emotion feature extraction failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_FEATURE_EXTRACTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class EmotionDatasetErrorException(BloopException):
    """Raised when the emotion reference corpus or training dataset is invalid or empty."""

    def __init__(self, message: str = "Emotion dataset error.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_DATASET_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class EmotionQNNTrainingFailedException(BloopException):
    """Raised when Hybrid QNN parameter optimization or training encounters an error."""

    def __init__(self, message: str = "Hybrid QNN training failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_QNN_TRAINING_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class EmotionQNNPredictionFailedException(BloopException):
    """Raised when forward pass inference on the Hybrid QNN fails."""

    def __init__(self, message: str = "Hybrid QNN prediction failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_QNN_PREDICTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class EmotionClassificationFailedException(BloopException):
    """Raised when mapping quantum expectation states to affective labels fails."""

    def __init__(self, message: str = "Emotion classification failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_CLASSIFICATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class EmotionRecommendationFailedException(BloopException):
    """Raised when the speech recommendation rule engine encounters an error."""

    def __init__(self, message: str = "Speech recommendation generation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_RECOMMENDATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class EmotionResourceLimitException(ValidationException):
    """Raised when text length, qubit count, or circuit depth exceeds emotion resource limits."""

    def __init__(self, message: str = "Emotion intelligence resource limit exceeded.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMOTION_RESOURCE_LIMIT",
            details=details,
        )


class UnsupportedEmotionModelException(ValidationException):
    """Raised when an unconfigured or unsupported emotion model or framework is requested."""

    def __init__(self, message: str = "Unsupported emotion model configuration.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="UNSUPPORTED_EMOTION_MODEL",
            details=details,
        )
