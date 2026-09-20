"""
Bloop Quantum Semantic Feature Reduction
Projects high-dimensional classical semantic vectors into quantum-compatible
low-dimensional spaces (N <= num_qubits) using TruncatedSVD and deterministic pooling.
"""

from typing import List, Optional, Tuple, Union
import numpy as np
from sklearn.decomposition import TruncatedSVD
from backend.app.quantum.semantic.exceptions import SemanticReductionFailedException


class SemanticDimensionalityReducer:
    """
    Reduces high-dimensional classical semantic features down to low-dimensional
    vectors suitable for qubit register encoding (2 <= target_dim <= 8).
    Strictly separates fit from transform to prevent semantic data leakage in benchmarks.
    """

    def __init__(self, target_dim: int = 4, method: str = "truncated_svd", random_state: int = 42):
        self.target_dim = max(2, min(target_dim, 8))
        self.method = method
        self.random_state = random_state
        self._is_fitted = False
        self._svd: Optional[TruncatedSVD] = None

    def fit(self, X: np.ndarray) -> "SemanticDimensionalityReducer":
        """
        Fits TruncatedSVD on training/reference vectors only (Zero Data Leakage guarantee).
        """
        try:
            X_arr = np.asarray(X, dtype=float)
            if X_arr.ndim == 1:
                X_arr = X_arr.reshape(1, -1)

            n_samples, n_features = X_arr.shape
            n_components = min(self.target_dim, n_features, max(1, n_samples - 1))

            self._svd = TruncatedSVD(n_components=n_components, random_state=self.random_state)
            self._svd.fit(X_arr)
            self._is_fitted = True
            return self
        except Exception as e:
            raise SemanticReductionFailedException(f"Dimensionality reduction fitting failed: {e}")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Projects vectors into target_dim space using the pre-fitted reducer.
        """
        try:
            X_arr = np.asarray(X, dtype=float)
            single_sample = False
            if X_arr.ndim == 1:
                single_sample = True
                X_arr = X_arr.reshape(1, -1)

            if self._is_fitted and self._svd is not None:
                reduced = self._svd.transform(X_arr)
                # If n_components < target_dim, zero-pad deterministically
                if reduced.shape[1] < self.target_dim:
                    pad_width = ((0, 0), (0, self.target_dim - reduced.shape[1]))
                    reduced = np.pad(reduced, pad_width, mode="constant")
            else:
                # Deterministic chunk pooling fallback if no fit dataset was provided
                reduced = np.array([self._deterministic_pool(row) for row in X_arr])

            return reduced[0] if single_sample else reduced
        except Exception as e:
            raise SemanticReductionFailedException(f"Dimensionality reduction transform failed: {e}")

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fits on X and returns transformed coordinates."""
        self.fit(X)
        return self.transform(X)

    def reduce_pair(self, vec_a: np.ndarray, vec_b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reduces a single pair of vectors for pairwise inference.
        Uses deterministic chunk-pooling or pre-fitted SVD.
        """
        try:
            if self._is_fitted and self._svd is not None:
                red_a = self.transform(vec_a)
                red_b = self.transform(vec_b)
                return red_a, red_b

            red_a = self._deterministic_pool(vec_a)
            red_b = self._deterministic_pool(vec_b)
            return red_a, red_b
        except Exception as e:
            raise SemanticReductionFailedException(f"Pairwise feature reduction failed: {e}")

    def _deterministic_pool(self, vec: np.ndarray) -> np.ndarray:
        """
        Deterministically pools a high-dimensional vector into target_dim buckets
        preserving relative energy across semantic feature bands without data leakage.
        """
        arr = np.asarray(vec, dtype=float).flatten()
        if len(arr) <= self.target_dim:
            padded = np.zeros(self.target_dim, dtype=float)
            padded[: len(arr)] = arr
            return padded

        chunk_size = len(arr) // self.target_dim
        pooled = np.zeros(self.target_dim, dtype=float)
        for i in range(self.target_dim):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < self.target_dim - 1 else len(arr)
            pooled[i] = np.mean(arr[start:end]) if end > start else 0.0
        return pooled

