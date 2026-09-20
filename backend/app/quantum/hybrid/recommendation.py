"""
Bloop Provider-Independent Speech Recommendation Service
Translates hybrid intelligence signals (affective classes, sentiment, and style)
into structured acoustic delivery recommendations.
Strictly decoupled: never calls external speech synthesis providers or triggers audio generation.
"""

from typing import Dict, Optional
from backend.app.quantum.hybrid.models import RecommendationPacing, SpeechRecommendationDTO


class HybridSpeechRecommender:
    """
    Translates hybrid classification and affective signals into acoustic speech recommendations.
    Enforces user autonomy: recommendations are suggestions only and never auto-applied.
    """

    CONFIDENCE_THRESHOLD = 0.35

    def generate_recommendation(
        self,
        predicted_class: str,
        class_scores: Dict[str, float],
        confidence: Optional[float] = None,
        target_voice_id: Optional[str] = None,
    ) -> SpeechRecommendationDTO:
        """
        Derives acoustic settings from hybrid classification.
        Conservative default is returned when confidence is low or ambiguous.
        """
        top_score = class_scores.get(predicted_class, 0.0)

        # Ambiguous or low-confidence gating: conservative balanced delivery
        if confidence is None or top_score < self.CONFIDENCE_THRESHOLD or confidence < self.CONFIDENCE_THRESHOLD:
            return SpeechRecommendationDTO(
                style="balanced",
                speed=1.0,
                pitch=1.0,
                stability=0.65,
                similarity_boost=0.75,
                pacing=RecommendationPacing.MODERATE.value,
                reason="Affective analysis indicates ambiguous sentiment; standard balanced delivery is recommended.",
                confidence=None,
                applied=False,
                target_voice_id=target_voice_id,
            )

        norm_class = predicted_class.lower()

        if norm_class in ["joy", "positive", "happy", "enthusiastic"]:
            return SpeechRecommendationDTO(
                style="expressive",
                speed=1.08,
                pitch=1.05,
                stability=0.50,
                similarity_boost=0.80,
                pacing=RecommendationPacing.DYNAMIC.value,
                reason="The analyzed text exhibits positive, upbeat indicators; an expressive tempo with dynamic inflection is recommended.",
                confidence=confidence,
                applied=False,
                target_voice_id=target_voice_id,
            )
        elif norm_class in ["sadness", "negative", "somber", "subdued"]:
            return SpeechRecommendationDTO(
                style="subdued",
                speed=0.92,
                pitch=0.95,
                stability=0.75,
                similarity_boost=0.75,
                pacing=RecommendationPacing.SLOW.value,
                reason="The analyzed text exhibits somber/subdued indicators; a slower, deliberate tempo with elevated stability is recommended.",
                confidence=confidence,
                applied=False,
                target_voice_id=target_voice_id,
            )
        elif norm_class in ["anger", "intense", "assertive", "urgent"]:
            return SpeechRecommendationDTO(
                style="intense",
                speed=1.12,
                pitch=1.08,
                stability=0.40,
                similarity_boost=0.85,
                pacing=RecommendationPacing.FAST.value,
                reason="The analyzed text exhibits assertive/intense textual traits; an energetic delivery with sharp emphasis is recommended.",
                confidence=confidence,
                applied=False,
                target_voice_id=target_voice_id,
            )
        elif norm_class in ["fear", "anxious", "cautious"]:
            return SpeechRecommendationDTO(
                style="cautious",
                speed=0.96,
                pitch=1.02,
                stability=0.60,
                similarity_boost=0.70,
                pacing=RecommendationPacing.MODERATE.value,
                reason="The analyzed text exhibits cautious indicators; measured pacing with moderate pitch elevation is recommended.",
                confidence=confidence,
                applied=False,
                target_voice_id=target_voice_id,
            )
        else:  # "neutral", "formal", etc.
            return SpeechRecommendationDTO(
                style="balanced",
                speed=1.0,
                pitch=1.0,
                stability=0.65,
                similarity_boost=0.75,
                pacing=RecommendationPacing.MODERATE.value,
                reason="The analyzed text exhibits balanced/neutral characteristics; standard natural delivery is recommended.",
                confidence=confidence,
                applied=False,
                target_voice_id=target_voice_id,
            )
