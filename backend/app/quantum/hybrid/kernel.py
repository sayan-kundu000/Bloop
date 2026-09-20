"""
Bloop Quantum Kernel Engine
Implements quantum kernel methods using Qiskit Machine Learning FidelityStatevectorKernel.
Provides exact statevector fidelity computation and kernel Gram matrix evaluation
for classical-to-quantum feature space projection.
"""

from typing import Any, Dict, List, Optional, Sequence, Union
import numpy as np

from backend.app.quantum.domain.models import QuantumFramework
from backend.app.quantum.exceptions import InvalidQuantumRequestException, QuantumExecutionError
from backend.app.quantum.hybrid.encoder import QuantumFeatureEncoder


class _DirectStatevectorKernel:
    """Direct Statevector fidelity kernel fallback for exact state transition simulation."""

    def __init__(self, feature_map):
        self.feature_map = feature_map

    def evaluate(self, x_vec: np.ndarray, y_vec: Optional[np.ndarray] = None) -> np.ndarray:
        from qiskit.quantum_info import Statevector

        sv_x = [Statevector.from_instruction(self.feature_map.assign_parameters(row)) for row in x_vec]
        if y_vec is None:
            n = len(sv_x)
            matrix = np.zeros((n, n), dtype=float)
            for i in range(n):
                matrix[i, i] = 1.0
                for j in range(i + 1, n):
                    fid = abs(np.vdot(sv_x[i].data, sv_x[j].data)) ** 2
                    matrix[i, j] = fid
                    matrix[j, i] = fid
            return matrix
        else:
            sv_y = [Statevector.from_instruction(self.feature_map.assign_parameters(row)) for row in y_vec]
            n_x = len(sv_x)
            n_y = len(sv_y)
            matrix = np.zeros((n_x, n_y), dtype=float)
            for i in range(n_x):
                for j in range(n_y):
                    matrix[i, j] = abs(np.vdot(sv_x[i].data, sv_y[j].data)) ** 2
            return matrix


class QuantumKernelEngine:
    """
    Qiskit Machine Learning Quantum Kernel Engine.
    Leverages zz_feature_map and FidelityStatevectorKernel for efficient,
    simulation-first quantum state space fidelity calculations.
    """

    def __init__(self, num_qubits: int = 4, reps: int = 1):
        self.num_qubits = max(2, min(num_qubits, 8))
        self.reps = max(1, min(reps, 3))
        self.encoder = QuantumFeatureEncoder(target_qubits=self.num_qubits)
        self._kernel = None

    def _init_kernel(self):
        if self._kernel is not None:
            return self._kernel

        try:
            try:
                from qiskit.circuit.library import ZZFeatureMap
                feature_map = ZZFeatureMap(feature_dimension=self.num_qubits, reps=self.reps)
            except (ImportError, AttributeError):
                from qiskit.circuit.library import zz_feature_map
                feature_map = zz_feature_map(feature_dimension=self.num_qubits, reps=self.reps)

            try:
                from qiskit_machine_learning.kernels import FidelityStatevectorKernel
                self._kernel = FidelityStatevectorKernel(feature_map=feature_map)
            except Exception:
                self._kernel = _DirectStatevectorKernel(feature_map=feature_map)

            return self._kernel
        except Exception as e:
            raise QuantumExecutionError(f"Failed to initialize Qiskit Machine Learning kernel: {e}")

    def evaluate_matrix(
        self,
        X: Union[List[List[float]], np.ndarray],
        Y: Optional[Union[List[List[float]], np.ndarray]] = None,
    ) -> List[List[float]]:
        """
        Computes the quantum kernel Gram matrix K(x_i, y_j) = |<phi(x_i)|phi(y_j)>|^2.
        All inputs are normalized into angle bounds [0, pi] before kernel evaluation.
        """
        kernel = self._init_kernel()

        X_arr = np.asarray(X, dtype=float)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(1, -1)

        # Normalize each sample to the target qubit dimension
        X_norm = np.array([self.encoder.normalize_to_angles(row) for row in X_arr])

        Y_norm = None
        if Y is not None:
            Y_arr = np.asarray(Y, dtype=float)
            if Y_arr.ndim == 1:
                Y_arr = Y_arr.reshape(1, -1)
            Y_norm = np.array([self.encoder.normalize_to_angles(row) for row in Y_arr])

        try:
            matrix = kernel.evaluate(x_vec=X_norm, y_vec=Y_norm)
            # Ensure return type is pure python floats
            return [[round(float(val), 6) for val in row] for row in matrix]
        except Exception as e:
            raise QuantumExecutionError(f"Quantum kernel matrix evaluation failed: {e}")

    def compute_fidelity(
        self,
        vec_a: Sequence[float],
        vec_b: Sequence[float],
    ) -> float:
        """
        Computes the pairwise transition fidelity |<phi(a)|phi(b)>|^2 between two feature vectors.
        """
        mat = self.evaluate_matrix([list(vec_a)], [list(vec_b)])
        return round(float(mat[0][0]), 6)
