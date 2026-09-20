"""
Audio Processing & Delivery Subsystem
Exports AudioProcessor, AudioDeliveryService, metadata models, and domain exceptions.
"""

from backend.app.services.audio.delivery import AudioDeliveryService
from backend.app.services.audio.exceptions import (
    AudioDeliveryException,
    AudioGenerationInvalidException,
    AudioNotFoundException,
    AudioProcessingException,
    GenerationAccessDeniedException,
    GenerationNotFoundException,
)
from backend.app.services.audio.models import (
    AudioMetadata,
    AudioValidationResult,
    ProcessedAudio,
)
from backend.app.services.audio.processor import AudioProcessor

__all__ = [
    "AudioProcessor",
    "AudioDeliveryService",
    "AudioMetadata",
    "AudioValidationResult",
    "ProcessedAudio",
    "AudioProcessingException",
    "AudioGenerationInvalidException",
    "AudioNotFoundException",
    "GenerationNotFoundException",
    "GenerationAccessDeniedException",
    "AudioDeliveryException",
]
