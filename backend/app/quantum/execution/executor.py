"""
Bloop Quantum Executor
Central orchestration engine for quantum simulations.
Manages adapter selection, resource limit enforcement, and timeout protection.
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Dict, Optional
from backend.app.quantum.config import quantum_config
from backend.app.quantum.domain.models import QuantumFramework
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.exceptions import (
    QuantumDisabledException,
    QuantumExecutionError,
    QuantumExecutionTimeoutException,
    UnsupportedFrameworkException,
)
from backend.app.quantum.execution.backend import QuantumBackend
from backend.app.quantum.qiskit.adapter import QiskitAdapter
from backend.app.quantum.pennylane.adapter import PennyLaneAdapter


class QuantumExecutor:
    """Dispatches quantum execution requests to the appropriate framework backend with timeout guards."""

    def __init__(self):
        self._qiskit_adapter = QiskitAdapter()
        self._pennylane_adapter = PennyLaneAdapter()

    def get_adapter(self, framework: str) -> QuantumBackend:
        """Resolves framework identifier to an instantiated adapter."""
        clean_fw = framework.lower().strip()
        if clean_fw == QuantumFramework.QISKIT.value:
            return self._qiskit_adapter
        elif clean_fw == QuantumFramework.PENNYLANE.value:
            return self._pennylane_adapter
        else:
            raise UnsupportedFrameworkException(
                framework=framework,
                supported=[QuantumFramework.QISKIT.value, QuantumFramework.PENNYLANE.value],
            )

    def execute(
        self,
        circuit: Any,
        framework: str = QuantumFramework.QISKIT.value,
        shots: int = 1024,
        seed: Optional[int] = None,
        noise_level: float = 0.0,
        timeout_seconds: Optional[float] = None,
        **kwargs: Any,
    ) -> NormalizedQuantumResult:
        """
        Executes a quantum experiment with enforced timeout protection.
        Raises:
            QuantumDisabledException: if QUANTUM_ENABLED is False.
            QuantumExecutionTimeoutException: if execution exceeds timeout.
            QuantumExecutionError: if simulation fails.
        """
        if not quantum_config.enabled:
            raise QuantumDisabledException("Quantum intelligence subsystem is disabled in this environment.")

        adapter = self.get_adapter(framework)
        max_time = timeout_seconds if timeout_seconds is not None else float(quantum_config.max_execution_time)

        # Execute inside a guarded thread pool to enforce hard wall-clock timeout
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                adapter.execute,
                circuit=circuit,
                shots=shots,
                seed=seed,
                noise_level=noise_level,
                **kwargs,
            )
            try:
                result = future.result(timeout=max_time)
                return result
            except FutureTimeoutError:
                raise QuantumExecutionTimeoutException(
                    f"Quantum execution timed out after {max_time} seconds.",
                    timeout_seconds=max_time,
                )
            except Exception as e:
                if isinstance(e, (QuantumExecutionError, QuantumExecutionTimeoutException)):
                    raise e
                raise QuantumExecutionError(str(e))
