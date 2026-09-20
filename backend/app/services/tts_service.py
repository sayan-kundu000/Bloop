"""
Bloop TTS Service (Backward-Compatibility Layer)
Exposes TTSService by subclassing SpeechService, ensuring existing endpoint routes,
domain callers, and test suites retain seamless interoperability.
"""

from typing import Optional
from sqlalchemy.orm import Session

from backend.app.providers.elevenlabs import ElevenLabsProvider
from backend.app.providers.mock_provider import MockTTSProvider
from backend.app.services.speech.service import SpeechService


class TTSService(SpeechService):
    """
    Backward-compatible TTS Service wrapper.
    Delegates completely to the modular SpeechService architecture.
    """

    def __init__(
        self,
        db: Session,
        elevenlabs_provider: Optional[ElevenLabsProvider] = None,
        mock_provider: Optional[MockTTSProvider] = None,
    ):
        super().__init__(
            db=db,
            elevenlabs_provider=elevenlabs_provider,
            mock_provider=mock_provider,
        )


__all__ = ["TTSService", "SpeechService", "ElevenLabsProvider", "MockTTSProvider"]
