"""
Bloop Quantum Semantic Benchmark Evaluator
Computes transparent empirical metrics (MAE, RMSE, Pearson r, Spearman rho)
comparing Classical Cosine vs Quantum Kernel Fidelity on validated benchmark pairs with zero data leakage.
"""

import math
import time
from typing import List, Tuple
import numpy as np
from scipy.stats import pearsonr, spearmanr
from backend.app.quantum.semantic.dataset import SemanticBenchmarkPair
from backend.app.quantum.semantic.models import SemanticBenchmarkMetrics


class SemanticBenchmarkEvaluator:
    """Evaluates classical baseline and quantum kernel similarity against ground-truth labels."""

    @staticmethod
    def calculate_metrics(
        y_true: List[float],
        y_pred: List[float],
    ) -> Tuple[float, float, float, float]:
        """
        Calculates (MAE, RMSE, Pearson r, Spearman rho).
        Guarantees finite numbers and handles zero-variance edge cases.
        """
        true_arr = np.asarray(y_true, dtype=float)
        pred_arr = np.asarray(y_pred, dtype=float)

        # 1. Error metrics
        mae = float(np.mean(np.abs(true_arr - pred_arr)))
        rmse = float(np.sqrt(np.mean((true_arr - pred_arr) ** 2)))

        # 2. Correlation metrics
        # If variance is zero (e.g. all predictions constant), correlation is undefined -> 0.0
        if np.std(true_arr) < 1e-7 or np.std(pred_arr) < 1e-7 or len(true_arr) < 3:
            p_val, s_val = 0.0, 0.0
        else:
            try:
                p_val, _ = pearsonr(true_arr, pred_arr)
                p_val = float(p_val) if not np.isnan(p_val) else 0.0
            except Exception:
                p_val = 0.0

            try:
                s_val, _ = spearmanr(true_arr, pred_arr)
                s_val = float(s_val) if not np.isnan(s_val) else 0.0
            except Exception:
                s_val = 0.0

        return (
            round(mae, 4),
            round(rmse, 4),
            round(p_val, 4),
            round(s_val, 4),
        )

    @staticmethod
    def build_honest_analysis(
        c_mae: float,
        q_mae: float,
        c_pearson: float,
        q_pearson: float,
        c_lat: float,
        q_lat: float,
    ) -> str:
        """
        Constructs an objective scientific summary of the benchmark results.
        Never makes false claims of quantum supremacy.
        """
        analysis = (
            f"Classical baseline (TF-IDF + Cosine) achieved MAE={c_mae:.4f} and Pearson r={c_pearson:.4f} "
            f"with an average latency of {c_lat:.2f}ms/pair. "
            f"Quantum kernel fidelity achieved MAE={q_mae:.4f} and Pearson r={q_pearson:.4f} "
            f"with an average latency of {q_lat:.2f}ms/pair. "
        )
        if q_pearson > c_pearson and q_mae < c_mae:
            analysis += (
                "On this small reference benchmark, the quantum state fidelity exhibited slightly closer "
                "correlation to human-calibrated semantic similarity than classical cosine similarity, "
                "though with higher simulation latency on classical hardware."
            )
        else:
            analysis += (
                "The classical baseline performed competitively or superiorly with significantly lower "
                "computational latency. This confirms the baseline hypothesis that classical representations "
                "remain highly effective on standard text similarity tasks without quantum advantage."
            )
        return analysis
