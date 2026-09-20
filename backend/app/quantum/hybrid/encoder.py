"""
Bloop Classical Feature Encoding & Normalization
Transforms classical numerical and text-derived feature vectors into quantum-compatible state angles.
Strictly validates numerical boundaries, finite values, and target qubit capacity.
"""

import math
from typing import List, Sequence, Union
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from backend.app.quantum.exceptions import InvalidQuantumRequestException


class QuantumFeatureEncoder:
    """Safe classical-to-quantum feature preprocessor and angle normalizer."""

    def __init__(self, target_qubits: int = 4):
        self.target_qubits = max(1, min(target_qubits, 8))
        self.scaler = MinMaxScaler(feature_range=(0.0, math.pi))

    def validate_features(self, features: Union[Sequence[float], np.ndarray]) -> np.ndarray:
        """Validates that numerical features are non-empty, finite, and 1D."""
        arr = np.asarray(features, dtype=float).flatten()
        if len(arr) == 0:
            raise InvalidQuantumRequestException(
                "Input feature array is empty.",
                details={"length": 0},
            )

        if not np.all(np.isfinite(arr)):
            raise InvalidQuantumRequestException(
                "Input features contain NaN or infinite values.",
                details={"has_nan": bool(np.isnan(arr).any()), "has_inf": bool(np.isinf(arr).any())},
            )

        return arr

    def normalize_to_angles(
        self,
        features: Union[Sequence[float], np.ndarray],
    ) -> List[float]:
        """
        Normalizes arbitrary input features to rotation angles in [0, pi]
        and projects to target_qubits dimensions.
        """
        arr = self.validate_features(features)

        # Pad or truncate to target_qubits dimensions
        if len(arr) < self.target_qubits:
            # Zero-pad
            padded = np.zeros(self.target_qubits, dtype=float)
            padded[: len(arr)] = arr
            arr = padded
        elif len(arr) > self.target_qubits:
            # Average down / truncate deterministically
            reshaped = arr[: self.target_qubits]
            arr = reshaped

        # Reshape for scikit-learn scaler
        reshaped_2d = arr.reshape(-1, 1)
        scaled = self.scaler.fit_transform(reshaped_2d).flatten()

        return [round(float(x), 6) for x in scaled]
