"""
Bloop Feature Normalization & Angle Mapping
Scales numerical features into bounded angular ranges [0, pi] suitable for
quantum rotation gates (Ry/Rx).
"""

import math
from typing import Optional, Union
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from backend.app.quantum.text.exceptions import FeatureEncodingFailedException


class FeatureAngleNormalizer:
    """
    Normalizes classical real-valued vectors into the compact interval [0, pi].
    This represents physical rotation angles for single-qubit Bloch sphere operations.
    """

    def __init__(self, min_angle: float = 0.0, max_angle: float = math.pi):
        if min_angle >= max_angle:
            raise ValueError("min_angle must be strictly less than max_angle.")
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.scaler = MinMaxScaler(feature_range=(self.min_angle, self.max_angle))
        self.is_fitted = False

    def validate_features(self, X: np.ndarray) -> np.ndarray:
        """Validates that input array is finite, non-empty, and contains no NaN or Inf."""
        if X is None or X.size == 0:
            raise FeatureEncodingFailedException("Feature array for normalization is empty.")
        if not np.all(np.isfinite(X)):
            raise FeatureEncodingFailedException(
                "Features contain invalid NaN or infinite values.",
                details={"has_nan": bool(np.isnan(X).any()), "has_inf": bool(np.isinf(X).any())},
            )
        return X

    def fit(self, X: np.ndarray) -> "FeatureAngleNormalizer":
        """
        Fits min-max scaling parameters strictly on training feature distributions.
        Prevents test-set distribution leakage.
        """
        valid_X = self.validate_features(X)
        try:
            self.scaler.fit(valid_X)
            self.is_fitted = True
            return self
        except Exception as e:
            raise FeatureEncodingFailedException(f"Failed to fit angle normalizer: {e}")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transforms features into angular interval [min_angle, max_angle].
        Clips extreme test outliers to ensure angle bounds are strictly respected.
        """
        valid_X = self.validate_features(X)
        if not self.is_fitted:
            # If not fitted in a batch pipeline, fit independently on the provided matrix/vector
            self.fit(valid_X)

        scaled = self.scaler.transform(valid_X)
        # Clip to ensure numerical bounds even with test-time distribution drift
        clipped = np.clip(scaled, self.min_angle, self.max_angle)
        return clipped

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fits on training data and returns normalized angles."""
        self.fit(X)
        return self.transform(X)

    @classmethod
    def normalize_single_vector(
        cls,
        vector: np.ndarray,
        min_angle: float = 0.0,
        max_angle: float = math.pi,
    ) -> np.ndarray:
        """
        Stateless utility to normalize an isolated 1D vector into [min_angle, max_angle].
        Useful for single inference requests.
        """
        arr = np.asarray(vector, dtype=float).flatten()
        if arr.size == 0:
            raise FeatureEncodingFailedException("Single vector for normalization is empty.")
        if not np.all(np.isfinite(arr)):
            raise FeatureEncodingFailedException("Single vector contains NaN or Inf.")

        v_min = np.min(arr)
        v_max = np.max(arr)
        if math.isclose(v_min, v_max, abs_tol=1e-9):
            # Flat vector: map to midpoint
            return np.full_like(arr, fill_value=(min_angle + max_angle) / 2.0)

        scaled = (arr - v_min) / (v_max - v_min)
        angles = min_angle + scaled * (max_angle - min_angle)
        return np.clip(angles, min_angle, max_angle)
