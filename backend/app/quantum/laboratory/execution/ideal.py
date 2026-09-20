"""
Bloop Ideal Simulator Executor
Executes ideal (noise-free) quantum circuits on Qiskit AerSimulator.
Computes measurement counts, normalized probability distributions, and statevector (for N <= 6).
"""

import time
from typing import Dict, List, Optional, Tuple
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from backend.app.quantum.laboratory.exceptions import QuantumExecutionError


class IdealSimulatorExecutor:
    """Simulates quantum circuits under ideal, noise-free unitary dynamics."""

    @classmethod
    def execute(
        cls,
        circuit: QuantumCircuit,
        shots: int = 1024,
        seed: Optional[int] = None,
        extract_statevector: bool = True,
    ) -> Tuple[Dict[str, int], Optional[List[str]], float]:
        """
        Runs ideal Aer simulation.
        Returns:
            Tuple of (counts_dict, statevector_amplitudes, execution_time_ms)
        """
        start_time = time.perf_counter()

        sim_kwargs = {}
        if seed is not None:
            sim_kwargs["seed_simulator"] = seed

        simulator = AerSimulator(**sim_kwargs)
        try:
            compiled = transpile(circuit, simulator, seed_transpiler=seed)
            job = simulator.run(compiled, shots=shots)
            result = job.result()
            counts = result.get_counts()
        except Exception as e:
            raise QuantumExecutionError(f"Ideal AerSimulator execution failed: {e}")

        # Optional Statevector calculation for low qubit counts (<= 6)
        state_repr: Optional[List[str]] = None
        if extract_statevector and circuit.num_qubits <= 6:
            try:
                # Build measurement-free circuit copy for pure statevector evolution
                qc_clean = circuit.remove_final_measurements(inplace=False)
                sv = Statevector.from_instruction(qc_clean)
                state_repr = [f"{round(c.real, 4):+0.4f}{round(c.imag, 4):+0.4f}j" for c in sv.data]
            except Exception:
                state_repr = None

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        return counts, state_repr, round(execution_time_ms, 2)
