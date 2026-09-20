"""
Bloop Distribution Visualization Transformer
Formats discrete probability comparisons and noise sweep curves into JSON-serializable,
visualization-ready structured data for frontend chart rendering.
"""

from typing import Any, Dict, List
from backend.app.quantum.laboratory.models import DistributionComparisonResult, RobustnessSweepResult


class DistributionVisualizer:
    """Transforms raw probability and robustness results into clean visualization schemas."""

    @classmethod
    def format_comparison_barchart(
        cls,
        comparison: DistributionComparisonResult,
    ) -> List[Dict[str, Any]]:
        """
        Formats side-by-side states comparison for bar charts.
        Returns a sorted list of state metrics.
        """
        return [
            {
                "state": item["state"],
                "ideal_probability": item["ideal_probability"],
                "noisy_probability": item["noisy_probability"],
                "divergence": item["divergence"],
                "ideal_count": item["ideal_count"],
                "noisy_count": item["noisy_count"],
            }
            for item in comparison.states_comparison
        ]

    @classmethod
    def format_robustness_linechart(
        cls,
        sweep: RobustnessSweepResult,
    ) -> List[Dict[str, Any]]:
        """
        Formats noise sweep points for multi-line progression charts.
        """
        return [
            {
                "noise_level": pt.parameter_value,
                "fidelity": pt.mean_fidelity,
                "fidelity_std": pt.std_fidelity,
                "tvd": pt.mean_tvd,
                "tvd_std": pt.std_tvd,
                "target_probability": pt.success_probability,
                "execution_time_ms": pt.execution_time_ms,
            }
            for pt in sweep.points
        ]
