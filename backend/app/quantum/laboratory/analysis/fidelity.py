"""
Bloop Fidelity Distinction & State Fidelity Analysis
Strictly preserves the foundational distinction between:
1. Quantum State Fidelity (|⟨ψ|φ⟩|² or Tr(√(√ρ σ √ρ))²)
2. Classical Measurement-Distribution Similarity (Bhattacharyya Coefficient Σ √(P(x)Q(x)))
"""

from typing import List, Optional
import numpy as np


class QuantumFidelityAnalyzer:
    """
    Handles state fidelity calculations when statevector or density matrix data is available,
    and documents mathematical differences against classical distribution similarity.
    """

    @classmethod
    def statevector_fidelity(cls, sv_a: List[complex], sv_b: List[complex]) -> float:
        """
        Computes pure quantum state fidelity:
        F(|ψ⟩, |φ⟩) = |⟨ψ|φ⟩|²
        Requires explicit complex amplitude vectors.
        """
        if len(sv_a) != len(sv_b) or len(sv_a) == 0:
            return 0.0

        vec_a = np.array(sv_a, dtype=complex)
        vec_b = np.array(sv_b, dtype=complex)

        # Normalize if necessary
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0

        vec_a = vec_a / norm_a
        vec_b = vec_b / norm_b

        inner_prod = np.vdot(vec_a, vec_b)
        fidelity = float(np.abs(inner_prod) ** 2)
        return round(min(max(fidelity, 0.0), 1.0), 5)

    @classmethod
    def get_fidelity_methodology_note(cls) -> str:
        """
        Returns an educational research note clarifying the distinction between
        quantum state fidelity and classical measurement distribution similarity.
        """
        return (
            "SCIENTIFIC NOTE: Measurement distribution similarity (Bhattacharyya coefficient) "
            "evaluates classical statistical overlap in the computational Z-basis. It does not "
            "capture quantum phase information or coherence. Quantum state fidelity (|⟨ψ|φ⟩|²) "
            "requires full state tomography or direct statevector evaluation."
        )
