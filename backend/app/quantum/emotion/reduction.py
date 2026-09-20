"""
Quantum Emotion Intelligence — Dimensionality Reducer
Projects high-dimensional sparse emotion feature matrices into target quantum dimensions (2 <= N <= 8)
using sparse-matrix-aware TruncatedSVD.
"""

from typing import Union
import numpy as np
from scipy.sparse import issparse, spmatrix
from sklearn.decomposition import TruncatedSVD
from backend.app.quantum.emotion.exceptions import EmotionResourceLimitException


class EmotionSVDReducer:
    """
    Reduces sparse emotion feature matrices to quantum-compatible dimensions.
    Avoids dense centering to preserve memory efficiency.
    """

    def __init__(self, target_dim: int = 4, random_state: int = 42):
        if target_dim < 2 or target_dim > 8:
            raise EmotionResourceLimitException(
                f"Target quantum dimension ({target_dim}) must be between 2 and 8."
            )
        self.target_dim = target_dim
        self.random_state = random_state
        self.svd: TruncatedSVD = None
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    def fit(self, X: Union[np.ndarray, spmatrix]) -> "EmotionSVDReducer":
        """
        Fits TruncatedSVD exclusively on training feature representations.
        """
        n_features = X.shape[1]
        n_components = min(self.target_dim, max(1, n_features - 1))

        self.svd = TruncatedSVD(
            n_components=n_components,
            algorithm="randomized",
            random_state=self.random_state,
        )
        self.svd.fit(X)
        self._is_fitted = True
        return self

    def transform(self, X: Union[np.ndarray, spmatrix]) -> np.ndarray:
        """
        Projects features into target_dim dimensions.
        Zero-pads if n_components < target_dim.
        """
        if not self._is_fitted:
            raise RuntimeError("EmotionSVDReducer must be fitted before transforming.")

        reduced = self.svd.transform(X)

        # Pad with zeros if reduced dimension is less than target_dim
        if reduced.shape[1] < self.target_dim:
            padding = np.zeros((reduced.shape[0], self.target_dim - reduced.shape[1]), dtype=np.float64)
            reduced = np.hstack([reduced, padding])

        return reduced[:, :self.target_dim]

    def fit_transform(self, X: Union[np.ndarray, spmatrix]) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
