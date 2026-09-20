"""
Bloop Speech Generation Legacy Import Alias
Re-exports SpeechGeneration from backend.app.models.speech_generation for backward compatibility.
"""

from backend.app.models.speech_generation import SpeechGeneration

__all__ = ["SpeechGeneration"]
