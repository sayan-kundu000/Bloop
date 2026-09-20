"""
Bloop Generation Repository Legacy Alias
Re-exports SpeechGenerationRepository as GenerationRepository for backward compatibility.
"""

from backend.app.repositories.speech_generation import SpeechGenerationRepository

# Legacy alias
GenerationRepository = SpeechGenerationRepository

__all__ = ["GenerationRepository", "SpeechGenerationRepository"]
