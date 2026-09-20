"""
Quantum Emotion Intelligence — Continuous Angle Normalizer
Scales reduced emotion feature vectors into continuous rotation angles [0, pi]
suitable for single-qubit Ry rotation gates, with strict NaN/Inf guards.
"""

import math
from typing import Union
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from backend.app.quantum.emotion.exceptions import EmotionAnalysisFailedException


class EmotionAngleNormalizer:
    """
    MinMax feature scaler mapping continuous features to [0, pi] rotation angles.
    Enforces strict mathematical bounds and rejects invalid numerical values.
    """

    def __init__(self, feature_min: float = 0.0, feature_max: float = math.pi):
        self.feature_range = (feature_min, feature_max)
        self.scaler = MinMaxScaler(feature_range=self.feature_range)
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    def _validate_input(self, X: np.ndarray) -> None:
        """Validates that numerical values are finite and non-empty."""
        if X is None or X.size == 0:
            raise EmotionAnalysisFailedException("Feature matrix for normalization cannot be empty.")

        if not np.all(np.isfinite(X)):
            raise EmotionAnalysisFailedException(
                "Feature matrix contains non-finite values (NaN or Inf), which cannot be normalized."
            )

    def fit(self, X: np.ndarray) -> "EmotionAngleNormalizer":
        """Fits MinMaxScaler exclusively on training split."""
        self._validate_input(X)
        self.scaler.fit(X)
        self._is_fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms features to [0, pi], clipping to safe bounds."""
        if not self._is_fitted:
            raise RuntimeError("EmotionAngleNormalizer must be fitted before transforming.")

        self._validate_input(X)
        scaled = self.scaler.transform(X)
        clipped = np.clip(scaled, self.feature_range[0], self.feature_range[1])
        return clipped

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
