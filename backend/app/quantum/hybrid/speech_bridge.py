"""
Bloop Speech Capability Bridge
Validates recommended speech settings against dynamic voice capabilities (Prompt 11)
and prepares provider-independent TTSRequest parameters without calling speech synthesis.
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.quantum.hybrid.exceptions import SpeechCapabilityMismatchException
from backend.app.quantum.hybrid.models import SpeechRecommendationDTO
from backend.app.services.capability_service import CapabilityService
from backend.app.services.voice_service import VoiceService


class SpeechCapabilityBridge:
    """
    Bridges hybrid speech recommendations with Bloop's dynamic voice architecture.
    Ensures suggestions are validated against voice-language capabilities before presenting to users.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.capability_service = CapabilityService(db) if db is not None else None
        self.voice_service = VoiceService(db) if db is not None else None

    def validate_and_enrich_recommendation(
        self,
        recommendation: SpeechRecommendationDTO,
        voice_id: Optional[str] = None,
        language: str = "en-US",
        strict: bool = False,
    ) -> SpeechRecommendationDTO:
        """
        Validates whether the target voice exists and supports the recommended settings.
        Never invents voice IDs or modifies immutable voice records.
        """
        if not voice_id or self.capability_service is None:
            # Standalone recommendation without voice binding
            recommendation.target_voice_id = voice_id
            recommendation.validated_compatible = True
            return recommendation

        try:
            # Query existing dynamic voice catalog
            voice, lang = self.capability_service.validate_tts_capability(
                voice_id=voice_id,
                language_code=language,
            )
            recommendation.target_voice_id = voice_id
            recommendation.validated_compatible = True
            return recommendation
        except Exception as e:
            logger.warning(f"Voice capability validation check failed for '{voice_id}': {e}")
            if strict:
                raise SpeechCapabilityMismatchException(
                    message=f"Voice '{voice_id}' does not support language '{language}' or required capabilities.",
                    details={"voice_id": voice_id, "language": language, "error": str(e)},
                )
            recommendation.target_voice_id = voice_id
            recommendation.validated_compatible = False
            recommendation.reason += f" (Note: Target voice '{voice_id}' capability compatibility could not be confirmed)."
            return recommendation

    @staticmethod
    def format_tts_payload(
        text: str,
        recommendation: SpeechRecommendationDTO,
        voice_id: str,
        language: str = "en-US",
    ) -> Dict[str, Any]:
        """
        Converts a recommendation into a validated, canonical TTSRequest payload
        for the standard POST /api/v1/tts endpoint upon user confirmation.
        """
        return {
            "text": text,
            "voice_id": voice_id,
            "language": language,
            "speed": round(recommendation.speed, 2),
            "pitch": round(recommendation.pitch, 2),
            "emotion": recommendation.style.capitalize(),
            "settings": {
                "stability": round(recommendation.stability, 2),
                "similarity_boost": round(recommendation.similarity_boost, 2),
                "style": 0.2 if recommendation.style == "expressive" else 0.0,
            },
        }
