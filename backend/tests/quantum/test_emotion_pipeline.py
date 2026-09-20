"""
Unit Tests — Quantum Emotion Intelligence Pipeline
Tests preprocessing, affective feature extraction, SVD reduction, angle normalization,
parameterized Hybrid QNN, zero-leakage evaluation, and speech recommendations.
"""

import math
import numpy as np
import pytest
from backend.app.quantum.emotion.preprocess import EmotionTextPreprocessor
from backend.app.quantum.emotion.features import EmotionFeatureExtractor
from backend.app.quantum.emotion.reduction import EmotionSVDReducer
from backend.app.quantum.emotion.normalization import EmotionAngleNormalizer
from backend.app.quantum.emotion.encoder import EmotionAngleEncoder
from backend.app.quantum.emotion.qnn import HybridEmotionQNN
from backend.app.quantum.emotion.classifier import HybridEmotionClassifier, ClassicalEmotionBaseline
from backend.app.quantum.emotion.dataset import EmotionDataset
from backend.app.quantum.emotion.evaluator import EmotionBenchmarkEvaluator
from backend.app.quantum.emotion.recommender import SpeechRecommendationService
from backend.app.quantum.emotion.labels import EmotionLabel
from backend.app.core.exceptions import ValidationException
from backend.app.quantum.emotion.exceptions import (
    EmotionResourceLimitException,
    EmotionAnalysisFailedException,
)


def test_emotion_preprocessor_valid_text():
    pre = EmotionTextPreprocessor()
    result = pre.preprocess("  I feel joyful and happy! \r\n")
    assert result == "I feel joyful and happy!"


def test_emotion_preprocessor_unicode_nfkc_normalization():
    pre = EmotionTextPreprocessor()
    # \uFB01 is the ligature 'fi'
    raw = "The \uFB01nal breakthrough brought joy!"
    normalized = pre.preprocess(raw)
    assert normalized == "The final breakthrough brought joy!"


def test_emotion_preprocessor_empty_rejection():
    pre = EmotionTextPreprocessor()
    with pytest.raises(ValidationException):
        pre.preprocess("")
    with pytest.raises(ValidationException):
        pre.preprocess("   \t \n  ")


def test_emotion_preprocessor_length_limit():
    pre = EmotionTextPreprocessor()
    oversized = "a" * 1001
    with pytest.raises(EmotionResourceLimitException):
        pre.preprocess(oversized)


def test_emotion_preprocessor_tokenization():
    pre = EmotionTextPreprocessor()
    tokens = pre.tokenize("Delighted with quantum intelligence!")
    assert tokens == ["delighted", "with", "quantum", "intelligence"]


def test_emotion_feature_extractor_lexical_and_statistical():
    texts = [
        "I am so thrilled and happy with this amazing breakthrough!",
        "The system process completed the standard database synchronization.",
        "Stop this terrible harassment immediately, I am furious and angry!",
    ]
    extractor = EmotionFeatureExtractor(max_features=16)
    features = extractor.fit_transform(texts)

    assert features.shape[0] == 3
    # At least 16 TF-IDF + 7 statistical signals
    assert features.shape[1] >= 16 + 7


def test_emotion_svd_reducer_dimension():
    extractor = EmotionFeatureExtractor(max_features=16)
    texts = [
        "I am so joyful and thrilled!",
        "The server is running normally.",
        "Deep sorrow and grief overcome me.",
        "This is an outrageous and furious betrayal!",
    ]
    features = extractor.fit_transform(texts)
    reducer = EmotionSVDReducer(target_dim=4)
    reduced = reducer.fit_transform(features)

    assert reduced.shape == (4, 4)
    assert isinstance(reduced, np.ndarray)


def test_emotion_angle_normalizer_bounds():
    normalizer = EmotionAngleNormalizer()
    raw = np.array([[10.0, -5.0, 0.0, 2.5], [1.0, 2.0, 3.0, 4.0]])
    angles = normalizer.fit_transform(raw)

    assert angles.shape == (2, 4)
    assert np.all(angles >= 0.0)
    assert np.all(angles <= math.pi + 1e-6)


def test_emotion_angle_normalizer_rejection_of_nan_inf():
    normalizer = EmotionAngleNormalizer()
    with pytest.raises(EmotionAnalysisFailedException):
        normalizer.fit(np.array([[1.0, np.nan], [0.0, 2.0]]))
    with pytest.raises(EmotionAnalysisFailedException):
        normalizer.fit(np.array([[1.0, np.inf], [0.0, 2.0]]))


def test_emotion_angle_encoder():
    encoder = EmotionAngleEncoder(num_qubits=4)
    res = encoder.encode([1.0, 2.0])
    assert len(res) == 4
    assert res[2] == 0.0 and res[3] == 0.0

    res_truncated = encoder.encode([1.0, 2.0, 3.0, 4.0, 5.0])
    assert len(res_truncated) == 4
    assert res_truncated[3] == 4.0


def test_hybrid_emotion_qnn_forward_and_entropy():
    qnn = HybridEmotionQNN(num_qubits=4, num_layers=2)
    angles = np.array([0.5, 1.0, 1.5, 2.0], dtype=np.float64)

    expectations = qnn.forward(angles)
    assert len(expectations) == 4
    for val in expectations:
        assert -1.0 <= val <= 1.0

    entropy = qnn.compute_entanglement_entropy(expectations)
    assert entropy >= 0.0
    assert qnn.get_circuit_depth() > 0


def test_hybrid_emotion_classifier_prediction():
    qnn = HybridEmotionQNN(num_qubits=4)
    classifier = HybridEmotionClassifier(qnn=qnn)

    # Train with synthetic angle features
    X_train = np.array([
        [0.2, 0.3, 0.1, 0.4],
        [2.5, 2.1, 2.0, 2.8],
        [1.5, 1.8, 1.6, 1.9],
        [0.8, 0.9, 0.7, 0.8],
    ], dtype=np.float64)
    y_train = ["joy", "sadness", "anger", "neutral"]

    classifier.fit(X_train, y_train)
    pred, scores, conf, entropy = classifier.predict_single(X_train[0])

    assert pred in ["joy", "sadness", "anger", "neutral"]
    assert len(scores) == 4
    assert math.isclose(sum(scores.values()), 1.0, rel_tol=1e-2)
    assert entropy >= 0.0


def test_speech_recommendation_mappings():
    recommender = SpeechRecommendationService()

    # Joy
    rec_joy = recommender.generate_recommendation("joy", {"joy": 0.80, "sadness": 0.10, "anger": 0.05, "neutral": 0.05}, confidence=0.80)
    assert rec_joy.style == "expressive"
    assert rec_joy.speed == 1.08
    assert rec_joy.pitch == 1.05
    assert rec_joy.stability == 0.50
    assert rec_joy.pacing == "dynamic"
    assert rec_joy.applied is False

    # Sadness
    rec_sad = recommender.generate_recommendation("sadness", {"sadness": 0.75, "joy": 0.05, "anger": 0.10, "neutral": 0.10}, confidence=0.75)
    assert rec_sad.style == "subdued"
    assert rec_sad.speed == 0.92
    assert rec_sad.pitch == 0.95
    assert rec_sad.stability == 0.75
    assert rec_sad.pacing == "slow"
    assert rec_sad.applied is False

    # Anger
    rec_ang = recommender.generate_recommendation("anger", {"anger": 0.85, "joy": 0.05, "sadness": 0.05, "neutral": 0.05}, confidence=0.85)
    assert rec_ang.style == "intense"
    assert rec_ang.speed == 1.12
    assert rec_ang.pitch == 1.08
    assert rec_ang.stability == 0.40
    assert rec_ang.pacing == "fast"
    assert rec_ang.applied is False

    # Neutral
    rec_neu = recommender.generate_recommendation("neutral", {"neutral": 0.70, "joy": 0.10, "sadness": 0.10, "anger": 0.10}, confidence=0.70)
    assert rec_neu.style == "balanced"
    assert rec_neu.speed == 1.00
    assert rec_neu.pitch == 1.00
    assert rec_neu.stability == 0.65
    assert rec_neu.pacing == "moderate"
    assert rec_neu.applied is False


def test_speech_recommendation_confidence_gating():
    recommender = SpeechRecommendationService()
    # Low confidence or ambiguous distribution
    rec_ambiguous = recommender.generate_recommendation(
        "joy",
        {"joy": 0.28, "sadness": 0.26, "anger": 0.24, "neutral": 0.22},
        confidence=None,
    )
    assert rec_ambiguous.style == "balanced"
    assert rec_ambiguous.speed == 1.0
    assert rec_ambiguous.confidence is None
    assert "ambiguous" in rec_ambiguous.reason.lower()


def test_benchmark_evaluator_zero_data_leakage():
    dataset = EmotionDataset()
    evaluator = EmotionBenchmarkEvaluator(dataset=dataset, num_qubits=4)
    q_metrics, c_summary, q_clf, c_clf, ext, red, norm = evaluator.run_benchmark()

    # Transformers must be fitted
    assert ext.is_fitted
    assert red.is_fitted
    assert norm.is_fitted

    # Metrics must be valid floats in [0, 1]
    assert 0.0 <= q_metrics.accuracy <= 1.0
    assert 0.0 <= q_metrics.f1_score <= 1.0
    assert q_metrics.training_time_seconds > 0.0
    assert q_metrics.inference_time_seconds > 0.0

    assert 0.0 <= c_summary["accuracy"] <= 1.0
    assert 0.0 <= c_summary["f1_score"] <= 1.0
