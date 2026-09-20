"""
Bloop Application Services — Quantum Service Facade
Re-exports the centralized QuantumService from the quantum domain services.
"""

from backend.app.quantum.services.quantum_service import QuantumService

__all__ = ["QuantumService"]
