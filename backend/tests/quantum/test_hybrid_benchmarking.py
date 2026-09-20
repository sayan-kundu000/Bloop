"""
Tests for Hybrid Intelligence Fusion, Classical Baselines, and Multi-Category Benchmarking
Verifies mathematical fusion correctness, train/test split hygiene, metric accuracy,
and resource limit enforcement.
"""

import pytest
import numpy as np

from backend.app.quantum.hybrid.fusion import HybridFusionEngine
from backend.app.quantum.hybrid.exceptions import (
    HybridFusionFailedException,
    BenchmarkResourceLimitException,
    BenchmarkInvalidException,
)
from backend.app.quantum.hybrid.benchmark import BenchmarkRunner
from backend.app.quantum.hybrid.models import BenchmarkCategory


def test_score_fusion_mathematics():
    """Verifies that score fusion computes a valid probability distribution and correct argmax."""
    classical = {"joy": 0.8, "sadness": 0.1, "neutral": 0.1}
    quantum = {"joy": 0.4, "sadness": 0.5, "neutral": 0.1}

    # Equal weighting (0.5, 0.5)
    best_class, conf, fused = HybridFusionEngine.fuse_scores(classical, quantum, alpha=0.5, beta=0.5)
    assert best_class == "joy"
    assert pytest.approx(fused["joy"], 0.01) == 0.60
    assert pytest.approx(fused["sadness"], 0.01) == 0.30
    assert pytest.approx(fused["neutral"], 0.01) == 0.10
    assert pytest.approx(sum(fused.values()), 0.01) == 1.0

    # Quantum-skewed weighting (0.2 classical, 0.8 quantum)
    quantum_sad = {"joy": 0.1, "sadness": 0.8, "neutral": 0.1}
    best_class_q, conf_q, fused_q = HybridFusionEngine.fuse_scores(classical, quantum_sad, alpha=0.2, beta=0.8)
    assert best_class_q == "sadness"
    assert pytest.approx(fused_q["sadness"], 0.01) == 0.66


def test_score_fusion_invalid_weights():
    """Verifies that fusion weights must sum to 1.0."""
    with pytest.raises(HybridFusionFailedException):
        HybridFusionEngine.fuse_scores({"joy": 0.5}, {"joy": 0.5}, alpha=0.7, beta=0.7)


def test_feature_fusion_normalization():
    """Verifies that concatenated hybrid feature vectors are L2-normalized."""
    c_vec = [1.0, 2.0, 3.0]
    q_vec = [0.5, 0.5, 0.5, 0.5]

    z = HybridFusionEngine.fuse_features(c_vec, q_vec, alpha=0.5, beta=0.5)
    norm = np.linalg.norm(z)
    assert pytest.approx(norm, 0.01) == 1.0
    assert len(z) == 7


def test_decision_fusion_gating():
    """Verifies consensus and confidence-gated decision rules."""
    # Unanimous agreement
    pred, conf, verdict = HybridFusionEngine.fuse_decisions("joy", 0.8, "joy", 0.7)
    assert pred == "joy"
    assert verdict == "unanimous_agreement"
    assert conf > 0.75

    # Quantum dominance when confidence delta exceeds threshold
    pred_q, conf_q, verdict_q = HybridFusionEngine.fuse_decisions("neutral", 0.4, "anger", 0.85, delta=0.15)
    assert pred_q == "anger"
    assert verdict_q == "quantum_dominance"


def test_benchmark_runner_type_a_text():
    """Verifies Type A text classification benchmark execution."""
    runner = BenchmarkRunner()
    res = runner.run_benchmark(
        category=BenchmarkCategory.TEXT_CLASSIFICATION.value,
        dataset_size=20,
        test_split=0.25,
        num_qubits=2,
        shots=128,
        random_seed=42,
    )

    assert res.category == BenchmarkCategory.TEXT_CLASSIFICATION.value
    assert res.classical_metrics.accuracy is not None
    assert res.quantum_metrics.accuracy is not None
    assert res.dataset.sample_count == 20
    assert res.dataset.test_count == 5
    assert res.honest_analysis is not None


def test_benchmark_runner_type_b_emotion():
    """Verifies Type B multi-class emotion QNN benchmark execution."""
    runner = BenchmarkRunner()
    res = runner.run_benchmark(
        category=BenchmarkCategory.EMOTION_QNN.value,
        dataset_size=16,
        test_split=0.25,
        num_qubits=4,
        shots=128,
        random_seed=42,
    )

    assert res.category == BenchmarkCategory.EMOTION_QNN.value
    assert res.classical_metrics.f1_score is not None
    assert res.quantum_metrics.f1_score is not None
    assert res.resource_usage["qubits"] == 4


def test_benchmark_runner_type_c_semantic():
    """Verifies Type C semantic similarity benchmark with hybrid fusion."""
    runner = BenchmarkRunner()
    res = runner.run_benchmark(
        category=BenchmarkCategory.SEMANTIC_SIMILARITY.value,
        num_qubits=2,
        shots=128,
        classical_weight=0.6,
        quantum_weight=0.4,
        random_seed=42,
    )

    assert res.category == BenchmarkCategory.SEMANTIC_SIMILARITY.value
    assert res.classical_metrics.mae is not None
    assert res.quantum_metrics.mae is not None
    assert res.hybrid_metrics is not None
    assert res.hybrid_metrics.mae is not None


def test_benchmark_runner_type_d_circuit():
    """Verifies Type D circuit noise benchmark execution."""
    runner = BenchmarkRunner()
    res = runner.run_benchmark(
        category=BenchmarkCategory.CIRCUIT_NOISE.value,
        num_qubits=2,
        shots=256,
        random_seed=42,
    )

    assert res.category == BenchmarkCategory.CIRCUIT_NOISE.value
    assert res.quantum_metrics.tvd is not None
    assert res.quantum_metrics.fidelity is not None
    assert 0.0 <= res.quantum_metrics.tvd <= 1.0


def test_benchmark_runner_type_e_pipeline():
    """Verifies Type E end-to-end hybrid speech pipeline benchmark."""
    runner = BenchmarkRunner()
    res = runner.run_benchmark(
        category=BenchmarkCategory.HYBRID_SPEECH_PIPELINE.value,
        num_qubits=2,
        shots=128,
        random_seed=42,
    )

    assert res.category == BenchmarkCategory.HYBRID_SPEECH_PIPELINE.value
    assert res.pipeline_breakdown is not None
    assert res.pipeline_breakdown.classical_ms >= 0.0
    assert res.pipeline_breakdown.quantum_ms >= 0.0
    assert res.pipeline_breakdown.fusion_ms >= 0.0
    assert res.pipeline_breakdown.total_ms > 0.0


def test_benchmark_resource_limits():
    """Verifies bounded computational limit guards."""
    runner = BenchmarkRunner()

    with pytest.raises(BenchmarkResourceLimitException):
        runner.run_benchmark(category="text_classification", dataset_size=500)

    with pytest.raises(BenchmarkResourceLimitException):
        runner.run_benchmark(category="text_classification", num_qubits=10)

    with pytest.raises(BenchmarkResourceLimitException):
        runner.run_benchmark(category="text_classification", shots=10000)


def test_benchmark_invalid_category():
    """Verifies rejection of unsupported benchmark category."""
    runner = BenchmarkRunner()
    with pytest.raises(BenchmarkInvalidException):
        runner.run_benchmark(category="arbitrary_unsupported_category")
