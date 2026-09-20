"""
Bloop Pluggable Semantic Similarity Engine
Provides modular similarity strategies (Classical Cosine, Quantum Kernel, Hybrid)
and neutral, calibrated interpretation of semantic divergence and match levels.
"""

from typing import Optional, Tuple
from backend.app.quantum.semantic.models import SemanticMethod, SimilarityVerdict


class SimilarityEngine:
    """Pluggable similarity computation and interpretation engine."""

    @staticmethod
    def interpret_verdict(score: float, is_identical_text: bool = False) -> SimilarityVerdict:
        """
        Maps a normalized similarity score in [0, 1] to a neutral, calibrated research verdict.
        Never makes unjustified claims about true cognitive understanding or semantic equivalence.
        """
        if is_identical_text or score >= 0.95:
            return SimilarityVerdict.IDENTICAL
        elif score >= 0.75:
            return SimilarityVerdict.STRONGLY_SIMILAR
        elif score >= 0.45:
            return SimilarityVerdict.MODERATELY_SIMILAR
        else:
            return SimilarityVerdict.DISSIMILAR

    @staticmethod
    def compute_hybrid_similarity(
        classical_sim: float,
        quantum_sim: float,
    ) -> Tuple[float, float]:
        """
        Computes the hybrid similarity score and divergence metric:
        hybrid = (classical + quantum) / 2.0
        divergence = |quantum - classical|
        """
        hybrid = round(float((classical_sim + quantum_sim) / 2.0), 6)
        divergence = round(float(abs(quantum_sim - classical_sim)), 6)
        return hybrid, divergence

    @staticmethod
    def resolve_score_and_verdict(
        method: SemanticMethod,
        classical_sim: float,
        quantum_sim: Optional[float],
        is_identical_text: bool = False,
    ) -> Tuple[float, Optional[float], float, SimilarityVerdict]:
        """
        Resolves the primary similarity score, hybrid score, divergence, and verdict based on selected method.
        Returns: (primary_score, hybrid_sim, divergence, verdict)
        """
        if method == SemanticMethod.CLASSICAL:
            primary_score = classical_sim
            hybrid_sim = None
            divergence = 0.0 if quantum_sim is None else round(abs(quantum_sim - classical_sim), 6)
            verdict = SimilarityEngine.interpret_verdict(primary_score, is_identical_text)
            return primary_score, hybrid_sim, divergence, verdict

        if method == SemanticMethod.QUANTUM:
            primary_score = quantum_sim if quantum_sim is not None else classical_sim
            hybrid_sim = None
            divergence = 0.0 if quantum_sim is None else round(abs(quantum_sim - classical_sim), 6)
            verdict = SimilarityEngine.interpret_verdict(primary_score, is_identical_text)
            return primary_score, hybrid_sim, divergence, verdict

        # Hybrid method (default)
        if quantum_sim is not None:
            hybrid_sim, divergence = SimilarityEngine.compute_hybrid_similarity(classical_sim, quantum_sim)
            primary_score = hybrid_sim
        else:
            hybrid_sim = None
            divergence = 0.0
            primary_score = classical_sim

        verdict = SimilarityEngine.interpret_verdict(primary_score, is_identical_text)
        return primary_score, hybrid_sim, divergence, verdict
