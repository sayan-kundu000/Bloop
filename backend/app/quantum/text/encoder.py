"""
Bloop Quantum Feature Encoding Abstraction
Maps classical normalized feature vectors into quantum state preparation parameters.
Provides angle encoding with mathematical boundary and dimension validation.
"""

import abc
import math
from typing import List, Sequence, Union
import numpy as np

from backend.app.quantum.text.exceptions import FeatureEncodingFailedException
from backend.app.quantum.text.normalization import FeatureAngleNormalizer


class BaseQuantumFeatureEncoder(abc.ABC):
    """Abstract interface for classical-to-quantum state encoders."""

    @abc.abstractmethod
    def encode(self, features: Union[Sequence[float], np.ndarray]) -> List[float]:
        """Encodes numerical features into quantum parameter angles."""
        pass

    @abc.abstractmethod
    def validate(self, features: Union[Sequence[float], np.ndarray]) -> np.ndarray:
        """Validates feature finiteness, shapes, and boundaries."""
        pass

    @property
    @abc.abstractmethod
    def required_qubits(self) -> int:
        """Returns the number of qubits required for this encoding."""
        pass


class AngleFeatureEncoder(BaseQuantumFeatureEncoder):
    """
    Angle Feature Encoder.
    Encodes an n-dimensional classical vector x into n single-qubit rotation angles
    theta_i = scale(x_i), applying |psi> = \bigotimes_{i=0}^{n-1} Ry(theta_i) |0>.
    """

    def __init__(self, target_qubits: int = 4):
        self._target_qubits = max(2, min(target_qubits, 8))

    @property
    def required_qubits(self) -> int:
        return self._target_qubits

    def validate(self, features: Union[Sequence[float], np.ndarray]) -> np.ndarray:
        """
        Validates that features are 1D, non-empty, and contain no NaN or Inf values.
        """
        arr = np.asarray(features, dtype=float).flatten()
        if arr.size == 0:
            raise FeatureEncodingFailedException("Feature vector cannot be empty.")
        if not np.all(np.isfinite(arr)):
            raise FeatureEncodingFailedException(
                "Feature vector contains NaN or infinite values.",
                details={"has_nan": bool(np.isnan(arr).any()), "has_inf": bool(np.isinf(arr).any())},
            )
        return arr

    def encode(self, features: Union[Sequence[float], np.ndarray]) -> List[float]:
        """
        Validates, adjusts dimensionality to required_qubits, and normalizes into [0, pi].
        Returns float angles suitable for rotation gates (Ry/Rx).
        """
        arr = self.validate(features)

        # Pad or truncate to target_qubits dimensions
        if len(arr) < self._target_qubits:
            padded = np.zeros(self._target_qubits, dtype=float)
            padded[: len(arr)] = arr
            arr = padded
        elif len(arr) > self._target_qubits:
            arr = arr[: self._target_qubits]

        # Normalize to [0, pi]
        angles = FeatureAngleNormalizer.normalize_single_vector(arr, min_angle=0.0, max_angle=math.pi)
        return [round(float(a), 6) for a in angles]
