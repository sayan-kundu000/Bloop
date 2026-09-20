"""
Bloop Benchmark Service
Orchestrates classical vs hybrid quantum-classical machine learning benchmarks.
"""

import numpy as np
from sklearn.datasets import make_classification

from backend.app.quantum.hybrid.classifier import HybridQuantumClassifier
from backend.app.quantum.execution.limits import validate_execution_parameters
from backend.app.schemas.quantum import (
    BenchmarkRequest,
    MetricComparison,
    QuantumBenchmarkResponse,
)


class BenchmarkService:
    """Service running empirical benchmark evaluations between classical and quantum ML."""

    def run_benchmark(self, req: BenchmarkRequest) -> QuantumBenchmarkResponse:
        """Executes a benchmark evaluation over a controlled dataset."""
        validate_execution_parameters(req.num_qubits, req.shots)

        # Generate a controlled synthetic classification problem
        X, y = make_classification(
            n_samples=req.dataset_size,
            n_features=req.num_qubits,
            n_informative=max(2, req.num_qubits - 1),
            n_redundant=1 if req.num_qubits > 2 else 0,
            n_classes=2,
            random_state=42,
        )

        classifier = HybridQuantumClassifier(
            num_qubits=req.num_qubits,
            shots=req.shots,
            seed=42,
        )

        res = classifier.evaluate(X, y, test_size=req.test_split)

        classical_metrics = MetricComparison(
            accuracy=res.classical_metrics.accuracy,
            precision=res.classical_metrics.precision,
            recall=res.classical_metrics.recall,
            f1_score=res.classical_metrics.f1_score,
            training_time_seconds=res.classical_metrics.training_time_seconds,
            inference_time_seconds=res.classical_metrics.inference_time_seconds,
        )

        quantum_metrics = MetricComparison(
            accuracy=res.quantum_metrics.accuracy,
            precision=res.quantum_metrics.precision,
            recall=res.quantum_metrics.recall,
            f1_score=res.quantum_metrics.f1_score,
            training_time_seconds=res.quantum_metrics.training_time_seconds,
            inference_time_seconds=res.quantum_metrics.inference_time_seconds,
        )

        summary = (
            f"Benchmark on {req.dataset_size} samples ({int(req.dataset_size * (1 - req.test_split))} train / "
            f"{int(req.dataset_size * req.test_split)} test) using {req.num_qubits} qubits. "
            f"Classical Accuracy: {res.classical_metrics.accuracy:.4f}, "
            f"Quantum Accuracy: {res.quantum_metrics.accuracy:.4f}."
        )

        return QuantumBenchmarkResponse(
            classical_model=res.classical_model_name,
            quantum_model=res.quantum_model_name,
            classical_metrics=classical_metrics,
            quantum_metrics=quantum_metrics,
            honest_analysis=res.honest_analysis,
            quantum_advantage_detected=res.quantum_advantage_detected,
            summary=summary,
        )
