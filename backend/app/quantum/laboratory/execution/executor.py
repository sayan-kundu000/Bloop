"""
Bloop Laboratory Executor Orchestrator
Coordinates guarded simulation dispatch across ideal and noisy backends with hard timeout protection.
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Dict, List, Optional, Tuple
from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

from backend.app.quantum.config import quantum_config
from backend.app.quantum.laboratory.exceptions import (
    LaboratoryResourceLimitException,
    QuantumExecutionTimeoutException,
    QuantumExecutionError,
)
from backend.app.quantum.laboratory.execution.ideal import IdealSimulatorExecutor
from backend.app.quantum.laboratory.execution.noisy import NoisySimulatorExecutor


class LaboratoryExecutor:
    """Manages thread-isolated simulation dispatch with timeout enforcement."""

    def __init__(self):
        self.max_timeout = float(quantum_config.max_execution_time)

    def execute_ideal(
        self,
        circuit: QuantumCircuit,
        shots: int = 1024,
        seed: Optional[int] = None,
        extract_statevector: bool = True,
        timeout_seconds: Optional[float] = None,
    ) -> Tuple[Dict[str, int], Optional[List[str]], float]:
        """Runs ideal simulation with timeout protection."""
        timeout = timeout_seconds if timeout_seconds is not None else self.max_timeout

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                IdealSimulatorExecutor.execute,
                circuit=circuit,
                shots=shots,
                seed=seed,
                extract_statevector=extract_statevector,
            )
            try:
                return future.result(timeout=timeout)
            except FutureTimeoutError:
                raise QuantumExecutionTimeoutException(
                    f"Ideal simulation timed out after {timeout} seconds.",
                    timeout_seconds=timeout,
                )
            except Exception as e:
                if isinstance(e, (QuantumExecutionError, QuantumExecutionTimeoutException)):
                    raise e
                raise QuantumExecutionError(str(e))

    def execute_noisy(
        self,
        circuit: QuantumCircuit,
        noise_model: NoiseModel,
        shots: int = 1024,
        seed: Optional[int] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Tuple[Dict[str, int], float]:
        """Runs noisy simulation with timeout protection."""
        timeout = timeout_seconds if timeout_seconds is not None else self.max_timeout

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                NoisySimulatorExecutor.execute,
                circuit=circuit,
                noise_model=noise_model,
                shots=shots,
                seed=seed,
            )
            try:
                return future.result(timeout=timeout)
            except FutureTimeoutError:
                raise QuantumExecutionTimeoutException(
                    f"Noisy simulation timed out after {timeout} seconds.",
                    timeout_seconds=timeout,
                )
            except Exception as e:
                if isinstance(e, (QuantumExecutionError, QuantumExecutionTimeoutException)):
                    raise e
                raise QuantumExecutionError(str(e))
