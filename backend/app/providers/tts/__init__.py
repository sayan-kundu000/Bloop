"""
Bloop TTS Provider Subsystem
"""

from backend.app.providers.tts.base import TTSProvider
from backend.app.providers.tts.elevenlabs import ElevenLabsProvider
from backend.app.providers.tts.simulation import SimulationTTSProvider
from backend.app.providers.tts.types import TTSGenerationOptions, ProviderSpeechResult

__all__ = [
    "TTSProvider",
    "ElevenLabsProvider",
    "SimulationTTSProvider",
    "TTSGenerationOptions",
    "ProviderSpeechResult",
]
