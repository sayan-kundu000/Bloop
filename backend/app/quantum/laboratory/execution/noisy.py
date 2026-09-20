"""
Bloop Noisy Simulator Executor
Executes quantum circuits on Qiskit AerSimulator under specified NoiseModel channels.
"""

import time
from typing import Dict, Optional, Tuple
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from backend.app.quantum.laboratory.exceptions import QuantumExecutionError


class NoisySimulatorExecutor:
    """Executes quantum circuits subjected to simulated decoherence and gate noise."""

    @classmethod
    def execute(
        cls,
        circuit: QuantumCircuit,
        noise_model: NoiseModel,
        shots: int = 1024,
        seed: Optional[int] = None,
    ) -> Tuple[Dict[str, int], float]:
        """
        Runs noisy Aer simulation.
        Returns:
            Tuple of (counts_dict, execution_time_ms)
        """
        start_time = time.perf_counter()

        sim_kwargs = {"noise_model": noise_model}
        if seed is not None:
            sim_kwargs["seed_simulator"] = seed

        simulator = AerSimulator(**sim_kwargs)
        try:
            compiled = transpile(circuit, simulator, seed_transpiler=seed)
            job = simulator.run(compiled, shots=shots)
            result = job.result()
            counts = result.get_counts()
        except Exception as e:
            raise QuantumExecutionError(f"Noisy AerSimulator execution failed: {e}")

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        return counts, round(execution_time_ms, 2)
