"""
Bloop Parameterized Quantum Circuit Builder
Constructs bounded, shallow variational quantum circuits with angle state preparation,
linear entanglement layers, and computational basis measurements.
"""

from typing import List, Optional, Tuple
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

from backend.app.quantum.text.exceptions import QuantumTextInvalidException


class TextQuantumCircuitBuilder:
    """
    Builds parameterized variational quantum circuits for text classification experiments.
    Enforces strict qubit (2 <= q <= 8) and depth boundaries.
    """

    def __init__(
        self,
        num_qubits: int = 4,
        circuit_depth: int = 2,
        entanglement: str = "linear",
    ):
        self.num_qubits = max(2, min(num_qubits, 8))
        self.circuit_depth = max(1, min(circuit_depth, 6))
        self.entanglement = entanglement

    def build_parameterized_circuit(self) -> Tuple[QuantumCircuit, ParameterVector, ParameterVector]:
        """
        Creates a symbolic parameterized Qiskit QuantumCircuit.
        Returns:
            (circuit, feature_parameters, weight_parameters)
        """
        x_params = ParameterVector("x", self.num_qubits)
        total_weights = self.num_qubits * self.circuit_depth
        w_params = ParameterVector("w", total_weights)

        qc = QuantumCircuit(self.num_qubits, self.num_qubits)

        # 1. State Preparation: Angle Encoding via Ry rotations
        for i in range(self.num_qubits):
            qc.ry(x_params[i], i)

        qc.barrier()

        # 2. Variational Entangling Layers
        weight_idx = 0
        for d in range(self.circuit_depth):
            # Entanglement
            if self.entanglement == "linear":
                for i in range(self.num_qubits - 1):
                    qc.cx(i, i + 1)
                if self.num_qubits > 2:
                    qc.cx(self.num_qubits - 1, 0)
            else:
                for i in range(self.num_qubits - 1):
                    qc.cx(i, i + 1)

            # Parameterized Rotations
            for i in range(self.num_qubits):
                qc.rz(w_params[weight_idx], i)
                weight_idx += 1

            qc.barrier()

        # 3. Measurement
        qc.measure(range(self.num_qubits), range(self.num_qubits))

        return qc, x_params, w_params

    def bind_circuit(
        self,
        features: List[float],
        weights: Optional[List[float]] = None,
    ) -> QuantumCircuit:
        """
        Builds and binds concrete numerical angles and variational weights into an executable circuit.
        """
        if len(features) != self.num_qubits:
            raise QuantumTextInvalidException(
                f"Feature vector length ({len(features)}) does not match qubit count ({self.num_qubits}).",
                details={"expected": self.num_qubits, "received": len(features)},
            )

        qc, x_params, w_params = self.build_parameterized_circuit()

        total_weights = len(w_params)
        if weights is None:
            # Deterministic, non-zero initial weights
            rng = np.random.RandomState(42)
            weights = (rng.uniform(0.1, 2 * np.pi, size=total_weights)).tolist()
        elif len(weights) != total_weights:
            # Adjust weights length deterministically
            if len(weights) < total_weights:
                weights = (weights * (total_weights // len(weights) + 1))[:total_weights]
            else:
                weights = weights[:total_weights]

        param_dict = {}
        for p, val in zip(x_params, features):
            param_dict[p] = float(val)
        for p, val in zip(w_params, weights):
            param_dict[p] = float(val)

        return qc.assign_parameters(param_dict)
