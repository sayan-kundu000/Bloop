"""
Bloop End-to-End Hybrid Quantum-Classical Pipeline
Implements the canonical dataflow:
Classical Input -> Feature Prep -> Normalization -> Quantum Encoding -> Execution -> Measurement -> Classical Output.
"""

from typing import Any, Dict, List, Optional, Sequence
import numpy as np

from backend.app.quantum.domain.models import QuantumFramework
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.hybrid.encoder import QuantumFeatureEncoder
from backend.app.quantum.execution.executor import QuantumExecutor
from backend.app.quantum.circuits.basic import build_bell_state


class HybridPipeline:
    """Coordinates classical feature preprocessing and quantum circuit transformation."""

    def __init__(self, num_qubits: int = 4, shots: int = 1024):
        self.num_qubits = num_qubits
        self.shots = shots
        self.encoder = QuantumFeatureEncoder(target_qubits=num_qubits)
        self.executor = QuantumExecutor()

    def process_vector(
        self,
        features: Sequence[float],
        experiment_id: Optional[str] = None,
    ) -> NormalizedQuantumResult:
        """
        Processes a numerical feature vector through the hybrid pipeline:
        1. Encodes features to rotation angles [0, pi]
        2. Constructs a parameterized quantum circuit
        3. Executes and returns normalized measurements
        """
        from qiskit import QuantumCircuit

        angles = self.encoder.normalize_to_angles(features)

        # Build parameterized Qiskit circuit
        qc = QuantumCircuit(self.num_qubits, self.num_qubits, name="hybrid_pipeline_circuit")
        for i, angle in enumerate(angles):
            qc.ry(angle, i)

        # Entanglement layer
        if self.num_qubits > 1:
            for i in range(self.num_qubits - 1):
                qc.cx(i, i + 1)

        qc.measure(range(self.num_qubits), range(self.num_qubits))

        result = self.executor.execute(
            circuit=qc,
            framework=QuantumFramework.QISKIT.value,
            shots=self.shots,
            experiment_id=experiment_id,
        )

        result.metrics = {
            "encoded_angles": angles,
            "feature_dim": len(features),
        }
        return result
