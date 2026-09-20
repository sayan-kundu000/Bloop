"""
Quantum Emotion Intelligence — Hybrid QNN Classifier & Classical Baseline
Trains a classical decision head over quantum expectation features, alongside
a parallel classical baseline (Logistic Regression) on identical train/test splits.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from backend.app.quantum.emotion.labels import EmotionLabel, EMOTION_LABELS
from backend.app.quantum.emotion.qnn import HybridEmotionQNN
from backend.app.quantum.emotion.exceptions import EmotionClassificationFailedException


class HybridEmotionClassifier:
    """
    Hybrid Quantum Neural Network Classifier.
    Maps quantum Pauli-Z expectation values to discrete emotion probability distributions.
    """

    def __init__(self, qnn: HybridEmotionQNN = None, random_state: int = 42):
        self.qnn = qnn or HybridEmotionQNN()
        self.classes_ = EMOTION_LABELS
        self.head: Optional[LogisticRegression] = None
        self._is_fitted = False
        self.random_state = random_state

    def fit(self, X_angles: np.ndarray, y: List[str]) -> "HybridEmotionClassifier":
        """
        Fits the hybrid decision head on quantum expectations derived from training inputs.
        """
        try:
            # 1. Forward pass through Quantum Neural Network to obtain expectation vectors
            quantum_features = self.qnn.forward_batch(X_angles)

            # 2. Train classical calibrated decision head
            self.head = LogisticRegression(
                max_iter=500,
                random_state=self.random_state,
                C=1.0,
            )
            self.head.fit(quantum_features, y)
            self.classes_ = list(self.head.classes_)
            self._is_fitted = True
            return self
        except Exception as e:
            raise EmotionClassificationFailedException(
                f"Failed to fit Hybrid Emotion Classifier: {str(e)}"
            )

    def predict_proba(self, X_angles: np.ndarray) -> np.ndarray:
        """
        Returns predicted probabilities for each emotion class.
        """
        if not self._is_fitted:
            # Fallback initialization if used for zero-shot single text before full benchmark
            # Map raw expectation values to direct probabilities
            expectations = self.qnn.forward_batch(X_angles)
            probs_list = []
            for exp in expectations:
                p = np.array([max((1.0 - float(val)) / 2.0, 0.05) for val in exp[:len(self.classes_)]])
                probs_list.append(p / np.sum(p))
            return np.array(probs_list)

        quantum_features = self.qnn.forward_batch(X_angles)
        return self.head.predict_proba(quantum_features)

    def predict_single(self, angle_vector: np.ndarray) -> Tuple[str, Dict[str, float], float, float]:
        """
        Infers emotion for a single normalized angle feature vector.
        Returns:
            (predicted_emotion, emotion_scores_dict, confidence, entanglement_entropy)
        """
        arr = np.asarray(angle_vector, dtype=np.float64).reshape(1, -1)
        expectations = self.qnn.forward(arr[0])
        entropy = self.qnn.compute_entanglement_entropy(expectations)

        probas = self.predict_proba(arr)[0]
        scores = {cls_name: round(float(probas[i]), 4) for i, cls_name in enumerate(self.classes_)}

        # Determine predicted class
        predicted_emotion = max(scores.items(), key=lambda x: x[1])[0]

        # Honest confidence calculation: margin between top probability and second
        sorted_probs = sorted(list(scores.values()), reverse=True)
        top_prob = sorted_probs[0]
        second_prob = sorted_probs[1] if len(sorted_probs) > 1 else 0.0
        margin = top_prob - second_prob

        # If model is ambiguous (low margin), reflect honest uncertainty
        confidence = round(top_prob, 4) if margin >= 0.05 else None

        return predicted_emotion, scores, confidence, entropy


class ClassicalEmotionBaseline:
    """
    Standard Classical Baseline (Logistic Regression on SVD features).
    Evaluated on identical train/test splits without data leakage.
    """

    def __init__(self, random_state: int = 42):
        self.model = LogisticRegression(max_iter=500, random_state=random_state)
        self.classes_ = EMOTION_LABELS
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: List[str]) -> "ClassicalEmotionBaseline":
        self.model.fit(X, y)
        self.classes_ = list(self.model.classes_)
        self._is_fitted = True
        return self

    def predict_single(self, feature_vector: np.ndarray) -> Tuple[str, float]:
        arr = np.asarray(feature_vector, dtype=np.float64).reshape(1, -1)
        if not self._is_fitted:
            return EmotionLabel.NEUTRAL.value, 0.50

        probas = self.model.predict_proba(arr)[0]
        top_idx = int(np.argmax(probas))
        pred = self.classes_[top_idx]
        conf = round(float(probas[top_idx]), 4)
        return pred, conf
