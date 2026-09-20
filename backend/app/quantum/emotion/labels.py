"""
Quantum Emotion Intelligence — Emotion Labels & Affective Taxonomy
Defines discrete affective categories, sentiment-vs-emotion distinctions, and taxonomy utilities.
"""

from enum import Enum
from typing import List, Dict


class EmotionLabel(str, Enum):
    """
    Validated Affective State Categories.
    Represents discrete emotional expressions modeled in the Hybrid QNN.
    """
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    NEUTRAL = "neutral"


class SentimentPolarity(str, Enum):
    """
    Broad Polarity Distinction.
    Sentiment reflects broad evaluative orientation (positive, negative, neutral),
    while Emotion represents specific physiological/affective registers.
    """
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# Taxonomy Metadata & Conceptual Boundaries
EMOTION_LABELS: List[str] = [e.value for e in EmotionLabel]

# Mapping discrete emotions to broad polarities for explainability
EMOTION_TO_POLARITY: Dict[EmotionLabel, SentimentPolarity] = {
    EmotionLabel.JOY: SentimentPolarity.POSITIVE,
    EmotionLabel.SADNESS: SentimentPolarity.NEGATIVE,
    EmotionLabel.ANGER: SentimentPolarity.NEGATIVE,
    EmotionLabel.NEUTRAL: SentimentPolarity.NEUTRAL,
}

# Scientific disclaimer regarding taxonomy limitations
TAXONOMY_LIMITATION_NOTE: str = (
    "The 4-class taxonomy (joy, sadness, anger, neutral) represents a controlled "
    "computational prototype. It is an experimental classification model and does not "
    "represent the full spectrum or nuance of human emotional experience."
)
