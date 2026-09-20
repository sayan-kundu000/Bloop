"""
Bloop Quantum Repository Legacy Alias
Re-exports QuantumExperimentRepository as QuantumRepository for backward compatibility.
"""

from backend.app.repositories.quantum_experiment import QuantumExperimentRepository

# Legacy alias
QuantumRepository = QuantumExperimentRepository

__all__ = ["QuantumRepository", "QuantumExperimentRepository"]
