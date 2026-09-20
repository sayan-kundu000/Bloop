"""
Provider Tests — BaseTTSProvider and SimulationTTSProvider
"""

import pytest
from backend.app.providers.simulation import SimulationTTSProvider


@pytest.mark.asyncio
async def test_simulation_provider_capabilities():
    provider = SimulationTTSProvider()
    assert provider.get_provider_name() == "simulation"
    assert provider.is_configured() is True


@pytest.mark.asyncio
async def test_simulation_provider_synthesis():
    provider = SimulationTTSProvider()
    audio_bytes = await provider.generate_speech(
        text="Testing simulation audio generation.",
        voice_id="batman-animated-2000"
    )
    assert isinstance(audio_bytes, (bytes, bytearray))
    assert len(audio_bytes) > 0
