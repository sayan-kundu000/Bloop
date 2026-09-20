"""
Quantum Emotion Intelligence — Speech Recommendation Service
Translates detected affective states into optional acoustic speech parameters.
Strictly decoupled: never automatically overrides user settings and never calls ElevenLabs.
"""

from typing import Dict, Optional
from backend.app.quantum.emotion.labels import EmotionLabel
from backend.app.quantum.emotion.models import SpeechRecommendation, RecommendationPacing


class SpeechRecommendationService:
    """
    Translates emotion classification results into suggested speech synthesis parameters.
    Ensures user autonomy: suggestions are presented for review and never auto-applied.
    """

    CONFIDENCE_THRESHOLD = 0.35

    def generate_recommendation(
        self,
        predicted_emotion: str,
        emotion_scores: Dict[str, float],
        confidence: Optional[float] = None,
    ) -> SpeechRecommendation:
        """
        Derives speech synthesis suggestions based on detected emotion and confidence.
        """
        top_score = emotion_scores.get(predicted_emotion, 0.0)

        # Ambiguous or low-confidence gating: recommend conservative default
        if confidence is None or top_score < self.CONFIDENCE_THRESHOLD:
            return SpeechRecommendation(
                style="balanced",
                speed=1.0,
                pitch=1.0,
                stability=0.65,
                similarity_boost=0.75,
                pacing=RecommendationPacing.MODERATE.value,
                reason="Emotion classification is ambiguous; conservative standard delivery is recommended.",
                confidence=None,
                applied=False,
            )

        if predicted_emotion == EmotionLabel.JOY.value:
            return SpeechRecommendation(
                style="expressive",
                speed=1.08,
                pitch=1.05,
                stability=0.50,
                similarity_boost=0.80,
                pacing=RecommendationPacing.DYNAMIC.value,
                reason="The analyzed text exhibits joyful affect; an expressive, slightly elevated tempo is recommended.",
                confidence=confidence,
                applied=False,
            )
        elif predicted_emotion == EmotionLabel.SADNESS.value:
            return SpeechRecommendation(
                style="subdued",
                speed=0.92,
                pitch=0.95,
                stability=0.75,
                similarity_boost=0.75,
                pacing=RecommendationPacing.SLOW.value,
                reason="The analyzed text exhibits subdued/sorrowful affect; a slower, more deliberate tempo and higher stability are recommended.",
                confidence=confidence,
                applied=False,
            )
        elif predicted_emotion == EmotionLabel.ANGER.value:
            return SpeechRecommendation(
                style="intense",
                speed=1.12,
                pitch=1.08,
                stability=0.40,
                similarity_boost=0.85,
                pacing=RecommendationPacing.FAST.value,
                reason="The analyzed text exhibits assertive/intense affect; an energetic delivery with dynamic emphasis is recommended.",
                confidence=confidence,
                applied=False,
            )
        else:  # NEUTRAL
            return SpeechRecommendation(
                style="balanced",
                speed=1.0,
                pitch=1.0,
                stability=0.65,
                similarity_boost=0.75,
                pacing=RecommendationPacing.MODERATE.value,
                reason="The analyzed text exhibits neutral affect; balanced standard delivery is recommended.",
                confidence=confidence,
                applied=False,
            )
