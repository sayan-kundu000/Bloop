"""
Bloop Quantum Subsystem Configuration
Provides encapsulated, validated configuration settings and execution limits
for the quantum intelligence subsystem.
"""

from typing import NamedTuple
from backend.app.core.config import settings


class QuantumLimits(NamedTuple):
    max_qubits: int
    max_shots: int
    max_execution_time_seconds: int
    default_shots: int
    max_text_features: int = 64
    text_circuit_depth: int = 4
    max_emotion_features: int = 32
    emotion_qubits: int = 4
    emotion_circuit_depth: int = 4
    emotion_layers: int = 2
    max_semantic_features: int = 64
    semantic_qubits: int = 4
    semantic_circuit_depth: int = 4
    semantic_max_pairs: int = 20
    max_circuit_depth: int = 30
    max_circuit_operations: int = 50
    max_sweep_steps: int = 10
    max_repeats: int = 5
    max_benchmark_samples: int = 150
    max_benchmark_runs: int = 10
    max_benchmark_qubits: int = 6
    max_benchmark_shots: int = 2048
    hybrid_default_classical_weight: float = 0.5
    hybrid_default_quantum_weight: float = 0.5


class QuantumConfig:
    """Access proxy to application quantum settings."""

    @property
    def enabled(self) -> bool:
        return getattr(settings, "QUANTUM_ENABLED", True)

    @property
    def max_qubits(self) -> int:
        return getattr(settings, "QUANTUM_MAX_QUBITS", 8)

    @property
    def max_shots(self) -> int:
        return getattr(settings, "QUANTUM_MAX_SHOTS", 8192)

    @property
    def default_shots(self) -> int:
        return getattr(settings, "QUANTUM_SIMULATOR_SHOTS", 1024)

    @property
    def max_execution_time(self) -> int:
        return getattr(settings, "QUANTUM_MAX_EXECUTION_TIME", 30)

    @property
    def max_text_features(self) -> int:
        return getattr(settings, "QUANTUM_TEXT_MAX_FEATURES", 64)

    @property
    def text_qubits(self) -> int:
        return getattr(settings, "QUANTUM_TEXT_QUBITS", 4)

    @property
    def text_circuit_depth(self) -> int:
        return getattr(settings, "QUANTUM_TEXT_CIRCUIT_DEPTH", 4)

    @property
    def max_emotion_features(self) -> int:
        return getattr(settings, "QUANTUM_EMOTION_MAX_FEATURES", 32)

    @property
    def emotion_qubits(self) -> int:
        return getattr(settings, "QUANTUM_EMOTION_QUBITS", 4)

    @property
    def emotion_circuit_depth(self) -> int:
        return getattr(settings, "QUANTUM_EMOTION_CIRCUIT_DEPTH", 4)

    @property
    def emotion_layers(self) -> int:
        return getattr(settings, "QUANTUM_EMOTION_LAYERS", 2)

    @property
    def max_semantic_features(self) -> int:
        return getattr(settings, "QUANTUM_SEMANTIC_MAX_FEATURES", 64)

    @property
    def semantic_qubits(self) -> int:
        return getattr(settings, "QUANTUM_SEMANTIC_QUBITS", 4)

    @property
    def semantic_circuit_depth(self) -> int:
        return getattr(settings, "QUANTUM_SEMANTIC_CIRCUIT_DEPTH", 4)

    @property
    def semantic_max_pairs(self) -> int:
        return getattr(settings, "QUANTUM_SEMANTIC_MAX_PAIRS", 20)

    @property
    def max_circuit_depth(self) -> int:
        return getattr(settings, "QUANTUM_MAX_CIRCUIT_DEPTH", 30)

    @property
    def max_circuit_operations(self) -> int:
        return getattr(settings, "QUANTUM_MAX_CIRCUIT_OPERATIONS", 50)

    @property
    def max_sweep_steps(self) -> int:
        return getattr(settings, "QUANTUM_MAX_SWEEP_STEPS", 10)

    @property
    def max_repeats(self) -> int:
        return getattr(settings, "QUANTUM_MAX_REPEATS", 5)

    @property
    def max_benchmark_samples(self) -> int:
        return getattr(settings, "QUANTUM_MAX_BENCHMARK_SAMPLES", 150)

    @property
    def max_benchmark_runs(self) -> int:
        return getattr(settings, "QUANTUM_MAX_BENCHMARK_RUNS", 10)

    @property
    def max_benchmark_qubits(self) -> int:
        return getattr(settings, "QUANTUM_MAX_BENCHMARK_QUBITS", 6)

    @property
    def max_benchmark_shots(self) -> int:
        return getattr(settings, "QUANTUM_MAX_BENCHMARK_SHOTS", 2048)

    @property
    def hybrid_default_classical_weight(self) -> float:
        return getattr(settings, "QUANTUM_HYBRID_CLASSICAL_WEIGHT", 0.5)

    @property
    def hybrid_default_quantum_weight(self) -> float:
        return getattr(settings, "QUANTUM_HYBRID_QUANTUM_WEIGHT", 0.5)

    @property
    def limits(self) -> QuantumLimits:
        return QuantumLimits(
            max_qubits=self.max_qubits,
            max_shots=self.max_shots,
            max_execution_time_seconds=self.max_execution_time,
            default_shots=self.default_shots,
            max_text_features=self.max_text_features,
            text_circuit_depth=self.text_circuit_depth,
            max_emotion_features=self.max_emotion_features,
            emotion_qubits=self.emotion_qubits,
            emotion_circuit_depth=self.emotion_circuit_depth,
            emotion_layers=self.emotion_layers,
            max_semantic_features=self.max_semantic_features,
            semantic_qubits=self.semantic_qubits,
            semantic_circuit_depth=self.semantic_circuit_depth,
            semantic_max_pairs=self.semantic_max_pairs,
            max_circuit_depth=self.max_circuit_depth,
            max_circuit_operations=self.max_circuit_operations,
            max_sweep_steps=self.max_sweep_steps,
            max_repeats=self.max_repeats,
            max_benchmark_samples=self.max_benchmark_samples,
            max_benchmark_runs=self.max_benchmark_runs,
            max_benchmark_qubits=self.max_benchmark_qubits,
            max_benchmark_shots=self.max_benchmark_shots,
            hybrid_default_classical_weight=self.hybrid_default_classical_weight,
            hybrid_default_quantum_weight=self.hybrid_default_quantum_weight,
        )


quantum_config = QuantumConfig()

