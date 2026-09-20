"""
Bloop Feature Dimensionality Reduction
Reduces high-dimensional classical TF-IDF matrices to small quantum-compatible dimensions.
Uses TruncatedSVD to preserve sparse representations without memory explosion.
"""

from typing import Optional, Union
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from backend.app.quantum.text.exceptions import FeatureReductionFailedException


class TruncatedSVDReducer:
    """
    Projects high-dimensional sparse or dense feature representations into a small
    latent space matching target quantum qubit register dimensions (2 <= n_components <= 8).
    """

    def __init__(self, target_dimension: int = 4, random_state: int = 42):
        self.target_dimension = max(2, min(target_dimension, 8))
        self.random_state = random_state
        self.svd: Optional[TruncatedSVD] = None
        self.is_fitted = False

    def fit(self, X: Union[sparse.spmatrix, np.ndarray]) -> "TruncatedSVDReducer":
        """
        Fits TruncatedSVD components strictly on training feature representations.
        Guarantees that test split data is never seen during reduction training.
        """
        try:
            n_features = X.shape[1]
            n_samples = X.shape[0]

            # SVD components cannot exceed min(n_samples - 1, n_features - 1)
            # If dataset or feature space is smaller than target_dimension, use min possible
            max_possible = max(1, min(n_samples - 1, n_features - 1))
            actual_components = min(self.target_dimension, max_possible)

            self.svd = TruncatedSVD(
                n_components=actual_components,
                random_state=self.random_state,
                algorithm="randomized",
            )
            self.svd.fit(X)
            self.is_fitted = True
            return self
        except Exception as e:
            raise FeatureReductionFailedException(
                f"Failed to fit TruncatedSVD: {e}",
                details={"target_dim": self.target_dimension, "input_shape": list(X.shape)},
            )

    def transform(self, X: Union[sparse.spmatrix, np.ndarray]) -> np.ndarray:
        """
        Projects input representations to target_dimension.
        Pads with zeros if fitted components were smaller than target_dimension.
        """
        if not self.is_fitted or self.svd is None:
            raise FeatureReductionFailedException("TruncatedSVDReducer must be fitted before transformation.")

        try:
            reduced = self.svd.transform(X)
            # If reduced dimension is smaller than target_dimension, zero-pad columns
            if reduced.shape[1] < self.target_dimension:
                padded = np.zeros((reduced.shape[0], self.target_dimension), dtype=float)
                padded[:, : reduced.shape[1]] = reduced
                return padded
            elif reduced.shape[1] > self.target_dimension:
                return reduced[:, : self.target_dimension]
            return reduced
        except Exception as e:
            raise FeatureReductionFailedException(f"Failed to project features via TruncatedSVD: {e}")

    def fit_transform(self, X: Union[sparse.spmatrix, np.ndarray]) -> np.ndarray:
        """Convenience method to fit and transform on training split."""
        self.fit(X)
        return self.transform(X)
