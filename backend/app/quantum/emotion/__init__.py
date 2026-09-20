"""
Bloop Quantum Emotion Intelligence Subsystem
Provides hybrid quantum-classical emotion intelligence, affective feature engineering,
trainable PennyLane variational QNN circuits, empirical classical baselines,
and user-controlled speech synthesis recommendations.
"""

from backend.app.quantum.emotion.labels import (
    EmotionLabel,
    SentimentPolarity,
    EMOTION_LABELS,
    EMOTION_TO_POLARITY,
    TAXONOMY_LIMITATION_NOTE,
)
from backend.app.quantum.emotion.exceptions import (
    EmotionAnalysisFailedException,
    EmotionFeatureExtractionFailedException,
    EmotionDatasetErrorException,
    EmotionQNNTrainingFailedException,
    EmotionQNNPredictionFailedException,
    EmotionClassificationFailedException,
    EmotionRecommendationFailedException,
    EmotionResourceLimitException,
    UnsupportedEmotionModelException,
)
from backend.app.quantum.emotion.models import (
    QNNFramework,
    RecommendationPacing,
    SpeechRecommendation,
    EmotionMetrics,
    EmotionClassificationResult,
)
from backend.app.quantum.emotion.schemas import (
    EmotionExperimentRequest,
    EmotionExperimentResponse,
    SpeechRecommendationPayload,
)
from backend.app.quantum.emotion.preprocess import EmotionTextPreprocessor
from backend.app.quantum.emotion.features import EmotionFeatureExtractor
from backend.app.quantum.emotion.reduction import EmotionSVDReducer
from backend.app.quantum.emotion.normalization import EmotionAngleNormalizer
from backend.app.quantum.emotion.encoder import EmotionAngleEncoder
from backend.app.quantum.emotion.qnn import HybridEmotionQNN
from backend.app.quantum.emotion.classifier import (
    HybridEmotionClassifier,
    ClassicalEmotionBaseline,
)
from backend.app.quantum.emotion.dataset import EmotionDataset
from backend.app.quantum.emotion.evaluator import EmotionBenchmarkEvaluator
from backend.app.quantum.emotion.recommender import SpeechRecommendationService
from backend.app.quantum.emotion.service import QuantumEmotionService

__all__ = [
    "EmotionLabel",
    "SentimentPolarity",
    "EMOTION_LABELS",
    "EMOTION_TO_POLARITY",
    "TAXONOMY_LIMITATION_NOTE",
    "EmotionAnalysisFailedException",
    "EmotionFeatureExtractionFailedException",
    "EmotionDatasetErrorException",
    "EmotionQNNTrainingFailedException",
    "EmotionQNNPredictionFailedException",
    "EmotionClassificationFailedException",
    "EmotionRecommendationFailedException",
    "EmotionResourceLimitException",
    "UnsupportedEmotionModelException",
    "QNNFramework",
    "RecommendationPacing",
    "SpeechRecommendation",
    "EmotionMetrics",
    "EmotionClassificationResult",
    "EmotionExperimentRequest",
    "EmotionExperimentResponse",
    "SpeechRecommendationPayload",
    "EmotionTextPreprocessor",
    "EmotionFeatureExtractor",
    "EmotionSVDReducer",
    "EmotionAngleNormalizer",
    "EmotionAngleEncoder",
    "HybridEmotionQNN",
    "HybridEmotionClassifier",
    "ClassicalEmotionBaseline",
    "EmotionDataset",
    "EmotionBenchmarkEvaluator",
    "SpeechRecommendationService",
    "QuantumEmotionService",
]
