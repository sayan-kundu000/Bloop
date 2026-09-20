"""
Bloop Classical Semantic Baseline
Implements robust, transparent classical Cosine Similarity and Semantic Distance
with strict zero-vector handling and finite normalization.
"""

from typing import Sequence, Union
import numpy as np
from backend.app.quantum.semantic.exceptions import SemanticSimilarityFailedException


class ClassicalSimilarityEngine:
    """
    Computes exact mathematical Cosine Similarity and Semantic Distance
    between semantic feature representations.
    """

    @staticmethod
    def compute_cosine_similarity(
        vec_a: Union[Sequence[float], np.ndarray],
        vec_b: Union[Sequence[float], np.ndarray],
        raw_text_a: str = "",
        raw_text_b: str = "",
    ) -> float:
        """
        Computes normalized Cosine Similarity:
        cos(A, B) = (A . B) / (||A|| ||B||)

        Safely handles:
        - Zero vectors
        - Identical texts with zero-norm features
        - Incompatible vector lengths (zero-padded)
        - Floating point precision boundaries in [0.0, 1.0]
        """
        try:
            a = np.asarray(vec_a, dtype=float).flatten()
            b = np.asarray(vec_b, dtype=float).flatten()

            # Align dimensions if necessary
            if len(a) != len(b):
                max_len = max(len(a), len(b))
                pad_a = np.zeros(max_len, dtype=float)
                pad_b = np.zeros(max_len, dtype=float)
                pad_a[: len(a)] = a
                pad_b[: len(b)] = b
                a, b = pad_a, pad_b

            norm_a = float(np.linalg.norm(a))
            norm_b = float(np.linalg.norm(b))

            if norm_a > 1e-7 and norm_b > 1e-7:
                dot_product = float(np.dot(a, b))
                sim = dot_product / (norm_a * norm_b)
            else:
                # If feature vectors are zero, check if texts are lexically identical
                clean_a = raw_text_a.strip().lower()
                clean_b = raw_text_b.strip().lower()
                if clean_a and clean_b and clean_a == clean_b:
                    sim = 1.0
                else:
                    sim = 0.0

            # Mathematical cosine between non-negative TF-IDF is in [0, 1]
            clamped = max(0.0, min(1.0, sim))
            return round(clamped, 6)
        except Exception as e:
            raise SemanticSimilarityFailedException(f"Classical cosine similarity computation failed: {e}")

    @staticmethod
    def compute_semantic_distance(similarity: float) -> float:
        """
        Computes distance interpretation assuming normalized similarity in [0, 1]:
        distance(A, B) = 1 - similarity(A, B)
        """
        clamped_sim = max(0.0, min(1.0, float(similarity)))
        distance = 1.0 - clamped_sim
        return round(max(0.0, min(1.0, distance)), 6)

    @staticmethod
    def compute_jaccard_token_similarity(text_a: str, text_b: str) -> float:
        """Computes lexical token Jaccard similarity as an auxiliary classical signal."""
        import re
        tokens_a = set(re.findall(r"\b\w+\b", text_a.lower()))
        tokens_b = set(re.findall(r"\b\w+\b", text_b.lower()))

        if not tokens_a and not tokens_b:
            return 1.0 if text_a.strip() == text_b.strip() else 0.0
        if not tokens_a or not tokens_b:
            return 0.0

        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        return round(float(intersection / union), 6) if union > 0 else 0.0
