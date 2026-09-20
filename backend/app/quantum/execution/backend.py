"""
Bloop Quantum Backend Interface
Defines the framework-agnostic contract for all quantum simulators and execution adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from backend.app.quantum.domain.result import NormalizedQuantumResult


class QuantumBackend(ABC):
    """Abstract quantum execution backend."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the canonical identifier for this backend."""
        pass

    @property
    @abstractmethod
    def framework(self) -> str:
        """Returns the underlying framework (qiskit, pennylane, etc.)."""
        pass

    @abstractmethod
    def execute(
        self,
        circuit: Any,
        shots: int,
        seed: Optional[int] = None,
        noise_level: float = 0.0,
        **kwargs: Any,
    ) -> NormalizedQuantumResult:
        """Executes a quantum circuit and returns a normalized result."""
        pass
