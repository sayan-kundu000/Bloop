"""
Bloop Distribution Comparison Metrics
Implements exact mathematical methods for comparing discrete probability distributions:
Total Variation Distance (TVD) and Bhattacharyya Classical Fidelity.
"""

import math
from typing import Any, Dict, List, Tuple
from backend.app.quantum.laboratory.models import DistributionComparisonResult
from backend.app.quantum.laboratory.analysis.measurements import MeasurementAnalyzer


class DistributionComparator:
    """Calculates statistical distance and similarity between probability distributions."""

    @classmethod
    def total_variation_distance(cls, p: Dict[str, float], q: Dict[str, float]) -> float:
        """
        Computes Total Variation Distance (TVD):
        TVD(P, Q) = 1/2 * Σ |P(x) - Q(x)|
        Bounded in [0.0, 1.0]. 0.0 indicates identical distributions; 1.0 indicates disjoint support.
        """
        all_keys = set(p.keys()).union(set(q.keys()))
        diff_sum = 0.0
        for k in all_keys:
            diff_sum += abs(p.get(k, 0.0) - q.get(k, 0.0))

        return round(0.5 * diff_sum, 5)

    @classmethod
    def classical_fidelity(cls, p: Dict[str, float], q: Dict[str, float]) -> float:
        """
        Computes Classical Fidelity / Bhattacharyya Coefficient:
        F(P, Q) = Σ √(P(x) * Q(x))
        Bounded in [0.0, 1.0]. 1.0 indicates identical distributions; 0.0 indicates orthogonal support.
        """
        all_keys = set(p.keys()).union(set(q.keys()))
        fid = 0.0
        for k in all_keys:
            p_val = p.get(k, 0.0)
            q_val = q.get(k, 0.0)
            if p_val > 0.0 and q_val > 0.0:
                fid += math.sqrt(p_val * q_val)

        return round(min(max(fid, 0.0), 1.0), 5)

    @classmethod
    def compare(
        cls,
        ideal_counts: Dict[str, int],
        noisy_counts: Dict[str, int],
        shots_ideal: int = 1024,
        shots_noisy: int = 1024,
    ) -> DistributionComparisonResult:
        """Performs full comparative analysis between ideal and noisy execution outcomes."""
        p_ideal = MeasurementAnalyzer.normalize_counts(ideal_counts, shots_ideal)
        p_noisy = MeasurementAnalyzer.normalize_counts(noisy_counts, shots_noisy)

        tvd = cls.total_variation_distance(p_ideal, p_noisy)
        fidelity = cls.classical_fidelity(p_ideal, p_noisy)

        ideal_entropy = MeasurementAnalyzer.calculate_shannon_entropy(p_ideal)
        noisy_entropy = MeasurementAnalyzer.calculate_shannon_entropy(p_noisy)

        dom_ideal, _ = MeasurementAnalyzer.get_dominant_state(p_ideal)
        dom_noisy, _ = MeasurementAnalyzer.get_dominant_state(p_noisy)

        # Build state-by-state comparison rows sorted by ideal probability descending
        all_states = sorted(set(p_ideal.keys()).union(set(p_noisy.keys())))
        states_data: List[Dict[str, Any]] = []
        max_div = 0.0

        for s in all_states:
            p_i = p_ideal.get(s, 0.0)
            p_n = p_noisy.get(s, 0.0)
            div = round(abs(p_i - p_n), 5)
            if div > max_div:
                max_div = div

            states_data.append({
                "state": s,
                "ideal_count": ideal_counts.get(s, 0),
                "noisy_count": noisy_counts.get(s, 0),
                "ideal_probability": p_i,
                "noisy_probability": p_n,
                "divergence": div,
            })

        states_data.sort(key=lambda x: x["ideal_probability"], reverse=True)

        return DistributionComparisonResult(
            total_variation_distance=tvd,
            classical_fidelity=fidelity,
            ideal_entropy=ideal_entropy,
            noisy_entropy=noisy_entropy,
            max_divergence=round(max_div, 5),
            dominant_ideal_state=dom_ideal,
            dominant_noisy_state=dom_noisy,
            states_comparison=states_data,
        )
