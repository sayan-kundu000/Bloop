"""
Bloop Quantum Intelligence & Hybrid Computing Subsystem
Provides foundational quantum simulation, gate-level experiments,
PennyLane differentiable circuits, and hybrid ML architectures.
"""

from backend.app.quantum.config import quantum_config, QuantumLimits
from backend.app.quantum.domain.models import (
    ExperimentType,
    QuantumFramework,
    ExecutionStatus,
    GateType,
    GateSpecification,
)
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.execution.backend import QuantumBackend
from backend.app.quantum.execution.executor import QuantumExecutor
from backend.app.quantum.execution.limits import (
    validate_qubits,
    validate_shots,
    validate_execution_parameters,
)
from backend.app.quantum.qiskit.adapter import QiskitAdapter
from backend.app.quantum.pennylane.adapter import PennyLaneAdapter
from backend.app.quantum.hybrid.encoder import QuantumFeatureEncoder
from backend.app.quantum.hybrid.classifier import HybridQuantumClassifier
from backend.app.quantum.hybrid.pipeline import HybridPipeline
from backend.app.quantum.hybrid.kernel import QuantumKernelEngine
from backend.app.quantum.services.quantum_service import QuantumService

# Backward-compatibility exports
from backend.app.quantum.text_classifier import QuantumTextClassifier
from backend.app.quantum.emotion_qnn import QuantumEmotionAnalyzer
from backend.app.quantum.semantic_kernel import QuantumSemanticEstimator
from backend.app.quantum.circuit_lab import QuantumCircuitLab
from backend.app.quantum.benchmarks import QuantumBenchmarkRunner

__all__ = [
    "quantum_config",
    "QuantumLimits",
    "ExperimentType",
    "QuantumFramework",
    "ExecutionStatus",
    "GateType",
    "GateSpecification",
    "NormalizedQuantumResult",
    "QuantumBackend",
    "QuantumExecutor",
    "validate_qubits",
    "validate_shots",
    "validate_execution_parameters",
    "QiskitAdapter",
    "PennyLaneAdapter",
    "QuantumFeatureEncoder",
    "HybridQuantumClassifier",
    "HybridPipeline",
    "QuantumKernelEngine",
    "QuantumService",
    # Legacy exports
    "QuantumTextClassifier",
    "QuantumEmotionAnalyzer",
    "QuantumSemanticEstimator",
    "QuantumCircuitLab",
    "QuantumBenchmarkRunner",
]
