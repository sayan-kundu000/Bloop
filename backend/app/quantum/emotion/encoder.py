"""
Quantum Emotion Intelligence — Angle Feature Encoder
Encodes continuous normalized angle features into single-qubit Ry rotation gate inputs.
Validates numerical constraints and register width boundaries.
"""

from typing import List, Union
import numpy as np
from backend.app.quantum.emotion.exceptions import EmotionResourceLimitException


class EmotionAngleEncoder:
    """
    Transforms normalized features into single-qubit Ry rotation parameters on n qubits.
    """

    def __init__(self, num_qubits: int = 4):
        if num_qubits < 2 or num_qubits > 8:
            raise EmotionResourceLimitException(
                f"Qubit count ({num_qubits}) must be between 2 and 8."
            )
        self.num_qubits = num_qubits

    def encode(self, features: Union[List[float], np.ndarray]) -> np.ndarray:
        """
        Validates, pads, or truncates a single feature vector to match num_qubits.
        Returns a float64 numpy array of length num_qubits.
        """
        arr = np.asarray(features, dtype=np.float64).flatten()

        if arr.size == 0:
            return np.zeros(self.num_qubits, dtype=np.float64)

        if not np.all(np.isfinite(arr)):
            raise ValueError("Cannot encode non-finite (NaN or Inf) feature values.")

        # Zero-pad or truncate to match register width
        if arr.size < self.num_qubits:
            padded = np.zeros(self.num_qubits, dtype=np.float64)
            padded[:arr.size] = arr
            return padded
        elif arr.size > self.num_qubits:
            return arr[:self.num_qubits]

        return arr
