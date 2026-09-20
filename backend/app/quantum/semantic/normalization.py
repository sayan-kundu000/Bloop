"""
Bloop Quantum Semantic Angle Normalization
Transforms reduced classical semantic vectors into continuous rotation angles
within [0, pi] for parameterized single-qubit Ry quantum gates.
"""

import math
from typing import List, Sequence, Union
import numpy as np
from backend.app.quantum.semantic.exceptions import SemanticEncodingFailedException


class SemanticAngleNormalizer:
    """
    Normalizes arbitrary continuous or reduced feature vectors into
    rotation angles theta in [0, pi].
    Guarantees finite numbers, NaN/Inf rejection, and explicit clipping.
    """

    def __init__(self, target_dim: int = 4):
        self.target_dim = max(2, min(target_dim, 8))

    def validate(self, features: Union[Sequence[float], np.ndarray]) -> np.ndarray:
        """Validates that feature vector is non-empty and finite."""
        arr = np.asarray(features, dtype=float).flatten()
        if len(arr) == 0:
            raise SemanticEncodingFailedException("Feature vector is empty.")
        if not np.all(np.isfinite(arr)):
            raise SemanticEncodingFailedException("Feature vector contains NaN or infinite values.")
        return arr

    def normalize(self, features: Union[Sequence[float], np.ndarray]) -> np.ndarray:
        """
        Normalizes feature vector into [0, pi] rotational angles:
        theta_i = pi * (0.5 * (x_i / ||x|| + 1.0) % 1.0)
        """
        arr = self.validate(features)

        # Pad or truncate to target_dim
        if len(arr) < self.target_dim:
            padded = np.zeros(self.target_dim, dtype=float)
            padded[: len(arr)] = arr
            arr = padded
        elif len(arr) > self.target_dim:
            arr = arr[: self.target_dim]

        norm = np.linalg.norm(arr)
        if norm > 1e-7:
            normalized = arr / norm
            # Map from [-1, 1] to [0, pi]
            angles = np.pi * 0.5 * (np.clip(normalized, -1.0, 1.0) + 1.0)
        else:
            # Zero vector maps to standard ground reference angles 0.0
            angles = np.zeros(self.target_dim, dtype=float)

        return np.clip(angles, 0.0, math.pi)

    def normalize_pair(
        self,
        vec_a: Union[Sequence[float], np.ndarray],
        vec_b: Union[Sequence[float], np.ndarray],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Normalizes a pair of feature vectors into quantum rotation angles."""
        return self.normalize(vec_a), self.normalize(vec_b)
