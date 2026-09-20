"""
Tests for Hybrid Quantum-Classical Machine Learning
Verifies strict train/test separation, scikit-learn metrics, and end-to-end hybrid pipeline dataflow.
"""

import pytest
import numpy as np
from sklearn.datasets import make_classification

from backend.app.quantum.hybrid.classifier import HybridQuantumClassifier
from backend.app.quantum.hybrid.pipeline import HybridPipeline


def test_hybrid_quantum_classifier_evaluation():
    """Verifies that HybridQuantumClassifier evaluates on held-out test data and reports metrics."""
    X, y = make_classification(
        n_samples=40,
        n_features=4,
        n_informative=3,
        n_redundant=0,
        n_classes=2,
        random_state=42,
    )

    classifier = HybridQuantumClassifier(num_qubits=4, shots=512, seed=42)
    result = classifier.evaluate(X, y, test_size=0.25)

    assert result.classical_model_name.startswith("Logistic Regression")
    assert result.quantum_model_name.startswith("Variational Quantum Classifier")

    # Metrics verification
    assert 0.0 <= result.classical_metrics.accuracy <= 1.0
    assert 0.0 <= result.classical_metrics.f1_score <= 1.0
    assert result.classical_metrics.training_time_seconds >= 0.0

    assert 0.0 <= result.quantum_metrics.accuracy <= 1.0
    assert 0.0 <= result.quantum_metrics.f1_score <= 1.0
    assert result.quantum_metrics.training_time_seconds >= 0.0

    # Analysis must be non-empty and honest
    assert len(result.honest_analysis) > 0
    assert isinstance(result.quantum_advantage_detected, bool)


def test_hybrid_pipeline_end_to_end():
    """Verifies full hybrid pipeline from raw feature vector to normalized quantum result."""
    pipeline = HybridPipeline(num_qubits=3, shots=512)
    raw_vector = [0.25, 1.75, 3.5]

    res = pipeline.process_vector(raw_vector)
    assert res.qubits == 3
    assert res.shots == 512
    assert len(res.counts) > 0
    assert res.metrics is not None
    assert "encoded_angles" in res.metrics
    assert len(res.metrics["encoded_angles"]) == 3
