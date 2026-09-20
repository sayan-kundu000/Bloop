"""
Bloop Mathematical Hybrid Intelligence Fusion Layer
Implements transparent, mathematically defined fusion algorithms:
- Score Fusion (Linear Convex Combination)
- Feature Fusion (L2-Normalized Weighted Concatenation)
- Decision Fusion (Confidence-Gated Argmax Rule)
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from backend.app.quantum.hybrid.exceptions import HybridFusionFailedException


class HybridFusionEngine:
    """Mathematical fusion engine combining classical and quantum intelligence signals."""

    @staticmethod
    def fuse_scores(
        classical_scores: Dict[str, float],
        quantum_scores: Dict[str, float],
        alpha: float = 0.5,
        beta: float = 0.5,
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Convex Score Fusion:
        P_hybrid(k) = alpha * P_classical(k) + beta * P_quantum(k)
        where alpha + beta = 1.0.
        Returns (predicted_class, confidence, fused_distribution).
        """
        if abs(alpha + beta - 1.0) > 1e-4:
            raise HybridFusionFailedException(f"Fusion weights must sum to 1.0 (alpha={alpha}, beta={beta}).")

        all_keys = set(classical_scores.keys()).union(set(quantum_scores.keys()))
        if not all_keys:
            return "neutral", 1.0, {"neutral": 1.0}

        fused: Dict[str, float] = {}
        for k in all_keys:
            c_val = classical_scores.get(k, 0.0)
            q_val = quantum_scores.get(k, 0.0)
            fused[k] = alpha * c_val + beta * q_val

        # Normalize to ensure valid probability simplex
        total = sum(fused.values())
        if total > 0:
            fused = {k: round(v / total, 4) for k, v in fused.items()}
        else:
            uniform = round(1.0 / len(all_keys), 4)
            fused = {k: uniform for k in all_keys}

        # Argmax decision
        best_class = max(fused.items(), key=lambda item: item[1])[0]
        confidence = fused[best_class]

        return best_class, confidence, fused

    @staticmethod
    def fuse_features(
        classical_vec: List[float],
        quantum_vec: List[float],
        alpha: float = 0.5,
        beta: float = 0.5,
    ) -> List[float]:
        """
        Normalized Feature Concatenation:
        z = [sqrt(alpha) * x_c_norm, sqrt(beta) * x_q_norm]
        """
        c_arr = np.array(classical_vec, dtype=np.float64)
        q_arr = np.array(quantum_vec, dtype=np.float64)

        c_norm = np.linalg.norm(c_arr)
        q_norm = np.linalg.norm(q_arr)

        c_unit = c_arr / c_norm if c_norm > 1e-9 else c_arr
        q_unit = q_arr / q_norm if q_norm > 1e-9 else q_arr

        z = np.concatenate([
            math.sqrt(alpha) * c_unit,
            math.sqrt(beta) * q_unit,
        ])
        z_norm = np.linalg.norm(z)
        if z_norm > 1e-9:
            z = z / z_norm

        return [round(float(v), 5) for v in z]

    @staticmethod
    def fuse_decisions(
        classical_pred: str,
        classical_conf: float,
        quantum_pred: str,
        quantum_conf: float,
        delta: float = 0.15,
    ) -> Tuple[str, float, str]:
        """
        Decision Fusion with Confidence Gating:
        If both agree -> accept agreement with boosted confidence.
        If they disagree -> if |conf_q - conf_c| > delta, favor higher confidence;
        otherwise mark as consensus compromise.
        """
        if classical_pred == quantum_pred:
            boosted = min(1.0, round(0.5 * (classical_conf + quantum_conf) + 0.1, 4))
            return classical_pred, boosted, "unanimous_agreement"

        diff = quantum_conf - classical_conf
        if diff > delta:
            return quantum_pred, quantum_conf, "quantum_dominance"
        elif -diff > delta:
            return classical_pred, classical_conf, "classical_dominance"
        else:
            # Ambiguous conflict: select classical as conservative fallback
            return classical_pred, round(0.5 * (classical_conf + quantum_conf), 4), "ambiguous_conflict_classical_fallback"
