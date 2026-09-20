"""
Bloop Measurement Analysis Utilities
Provides normalization, Shannon entropy, dominant state detection,
and statistical summaries for discrete quantum measurement outcomes.
"""

import math
from typing import Dict, Tuple
from backend.app.quantum.laboratory.models import MeasurementSummary


class MeasurementAnalyzer:
    """Calculates statistical and information-theoretic metrics on measurement distributions."""

    @classmethod
    def normalize_counts(cls, counts: Dict[str, int], shots: int) -> Dict[str, float]:
        """Converts raw integer counts into a probability distribution summing to 1.0."""
        if shots <= 0:
            shots = max(sum(counts.values()), 1)

        probabilities = {}
        for state, count in counts.items():
            probabilities[state] = round(count / shots, 5)
        return probabilities

    @classmethod
    def calculate_shannon_entropy(cls, probabilities: Dict[str, float]) -> float:
        """
        Computes Shannon entropy: H = -Σ P(x) * log2(P(x)).
        Measures information uncertainty / state dispersion in bits.
        """
        entropy = 0.0
        for p in probabilities.values():
            if p > 1e-9:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @classmethod
    def get_dominant_state(cls, probabilities: Dict[str, float]) -> Tuple[str, float]:
        """Identifies the basis state with maximum measured probability."""
        if not probabilities:
            return "", 0.0

        max_state = max(probabilities.items(), key=lambda item: item[1])
        return max_state[0], max_state[1]

    @classmethod
    def summarize(cls, counts: Dict[str, int], shots: int) -> MeasurementSummary:
        """Produces a comprehensive statistical summary of measurement counts."""
        probs = cls.normalize_counts(counts, shots)
        dominant_state, dominant_prob = cls.get_dominant_state(probs)
        entropy = cls.calculate_shannon_entropy(probs)
        support_size = sum(1 for p in probs.values() if p > 0.0)

        return MeasurementSummary(
            counts=counts,
            probabilities=probs,
            dominant_state=dominant_state,
            dominant_probability=dominant_prob,
            entropy=entropy,
            support_size=support_size,
        )
