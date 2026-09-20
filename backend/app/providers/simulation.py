"""
Simulation TTS Provider Module
Provides offline synthetic audio generation when ElevenLabs API keys are not present.
"""

from backend.app.providers.mock_provider import MockTTSProvider

# Canonical alias as specified in system architecture
SimulationTTSProvider = MockTTSProvider

__all__ = ["SimulationTTSProvider", "MockTTSProvider"]
