"""
Unit and Component Tests for Bloop Quantum Semantic Intelligence Pipeline
Tests: preprocessing, feature extraction, TruncatedSVD reduction, angle normalization,
angle encoding, classical baseline, quantum transition fidelity, hybrid similarity, dataset adapter, and evaluator.
"""

import numpy as np
import pytest

from backend.app.quantum.semantic.classical import ClassicalSimilarityEngine
from backend.app.quantum.semantic.dataset import SemanticDatasetAdapter
from backend.app.quantum.semantic.evaluator import SemanticBenchmarkEvaluator
from backend.app.quantum.semantic.exceptions import (
    SemanticEncodingFailedException,
    SemanticInputInvalidException,
    SemanticResourceLimitException,
)
from backend.app.quantum.semantic.features import (
    LexicalFeatureProvider,
    SemanticFeatureExtractor,
    TfidfFeatureProvider,
)
from backend.app.quantum.semantic.models import SemanticMethod, SimilarityVerdict
from backend.app.quantum.semantic.normalization import SemanticAngleNormalizer
from backend.app.quantum.semantic.preprocess import SemanticPreprocessor
from backend.app.quantum.semantic.quantum_encoder import AngleFeatureEncoder
from backend.app.quantum.semantic.quantum_kernel import QuantumKernelEngine
from backend.app.quantum.semantic.reduction import SemanticDimensionalityReducer
from backend.app.quantum.semantic.schemas import (
    SemanticAnalysisRequest,
    SemanticBenchmarkRequest,
    SemanticMatrixRequest,
)
from backend.app.quantum.semantic.service import QuantumSemanticService
from backend.app.quantum.semantic.similarity import SimilarityEngine


class TestSemanticPreprocessing:
    def test_clean_text_nfkc_and_whitespace(self):
        prep = SemanticPreprocessor(max_length=500)
        raw = "  Hello\u00A0 \t\nWorld!  \r\n"
        cleaned = prep.clean_text(raw)
        assert cleaned == "Hello World!"

    def test_validate_pair_success(self):
        prep = SemanticPreprocessor()
        a, b = prep.validate_pair("First prompt.", "Second prompt.")
        assert a == "First prompt."
        assert b == "Second prompt."

    def test_validate_pair_empty_rejected(self):
        prep = SemanticPreprocessor()
        with pytest.raises(SemanticInputInvalidException) as exc_info:
            prep.validate_pair("", "Valid text")
        assert "text_a" in str(exc_info.value.details)

        with pytest.raises(SemanticInputInvalidException) as exc_info:
            prep.validate_pair("Valid text", "   \t\n  ")
        assert "text_b" in str(exc_info.value.details)

    def test_validate_pair_length_exceeded(self):
        prep = SemanticPreprocessor(max_length=50)
        with pytest.raises(SemanticInputInvalidException):
            prep.validate_pair("a" * 51, "Valid text")


class TestSemanticFeatures:
    def test_tfidf_feature_provider(self):
        provider = TfidfFeatureProvider(max_features=32)
        assert provider.feature_dimension > 0
        assert "TF-IDF" in provider.representation_name

        vec = provider.extract_features("Quantum speech synthesis platform.")
        assert isinstance(vec, np.ndarray)
        assert len(vec) == provider.feature_dimension
        assert np.any(vec > 0)

    def test_lexical_feature_provider(self):
        provider = LexicalFeatureProvider(feature_dim=16)
        vec = provider.extract_features("Is speech synthesis exciting? Yes!")
        assert len(vec) == 16
        assert np.all(np.isfinite(vec))

    def test_semantic_feature_extractor_facade(self):
        extractor = SemanticFeatureExtractor(max_features=32)
        vec_a, vec_b = extractor.extract_pair("Speech synthesis", "Audio voice generation")
        assert len(vec_a) == len(vec_b)
        assert len(vec_a) == extractor.feature_dimension


class TestSemanticReduction:
    def test_truncated_svd_reduction(self):
        reducer = SemanticDimensionalityReducer(target_dim=4)
        # Mock high-dimensional feature matrix (10 samples, 32 features)
        X = np.random.RandomState(42).rand(10, 32)
        reducer.fit(X)
        transformed = reducer.transform(X[:2])
        assert transformed.shape == (2, 4)

    def test_deterministic_pooling_fallback(self):
        reducer = SemanticDimensionalityReducer(target_dim=4)
        vec = np.ones(32)
        pooled = reducer._deterministic_pool(vec)
        assert len(pooled) == 4
        assert np.allclose(pooled, [1.0, 1.0, 1.0, 1.0])

    def test_reduce_pair(self):
        reducer = SemanticDimensionalityReducer(target_dim=4)
        v_a = np.ones(16)
        v_b = np.zeros(16)
        r_a, r_b = reducer.reduce_pair(v_a, v_b)
        assert len(r_a) == 4
        assert len(r_b) == 4


class TestSemanticNormalization:
    def test_angle_normalizer_bounds(self):
        normalizer = SemanticAngleNormalizer(target_dim=4)
        vec = np.array([0.5, -0.2, 1.5, 0.0])
        angles = normalizer.normalize(vec)
        assert len(angles) == 4
        assert np.all(angles >= 0.0)
        assert np.all(angles <= np.pi)

    def test_nan_inf_rejection(self):
        normalizer = SemanticAngleNormalizer(target_dim=4)
        with pytest.raises(SemanticEncodingFailedException):
            normalizer.normalize(np.array([1.0, np.nan, 2.0]))

        with pytest.raises(SemanticEncodingFailedException):
            normalizer.normalize(np.array([1.0, np.inf, 2.0]))


class TestClassicalBaseline:
    def test_identical_texts_give_maximum_cosine_similarity(self):
        vec = np.array([0.5, 0.5, 0.5])
        sim = ClassicalSimilarityEngine.compute_cosine_similarity(vec, vec, "text", "text")
        assert sim == 1.0

    def test_orthogonal_vectors_give_zero_similarity(self):
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([0.0, 1.0])
        sim = ClassicalSimilarityEngine.compute_cosine_similarity(vec_a, vec_b)
        assert sim == 0.0

    def test_zero_vector_handling(self):
        vec_zero = np.zeros(4)
        vec_nonzero = np.array([1.0, 2.0, 3.0, 4.0])

        # Different texts with zero vector -> 0.0
        sim_diff = ClassicalSimilarityEngine.compute_cosine_similarity(
            vec_zero, vec_nonzero, "hello", "world"
        )
        assert sim_diff == 0.0

        # Identical texts with zero vector -> 1.0
        sim_same = ClassicalSimilarityEngine.compute_cosine_similarity(
            vec_zero, vec_zero, "identical", "identical"
        )
        assert sim_same == 1.0

    def test_semantic_distance(self):
        assert ClassicalSimilarityEngine.compute_semantic_distance(1.0) == 0.0
        assert ClassicalSimilarityEngine.compute_semantic_distance(0.0) == 1.0
        assert ClassicalSimilarityEngine.compute_semantic_distance(0.75) == 0.25


class TestQuantumKernel:
    def test_angle_feature_encoder(self):
        encoder = AngleFeatureEncoder(num_qubits=4)
        angles = [0.1, 0.2, 0.3, 0.4]
        qc = encoder.encode_circuit(angles)
        assert qc.num_qubits == 4
        assert qc.depth() > 0

    def test_qiskit_quantum_kernel_identical_fidelity(self):
        kernel = QuantumKernelEngine(num_qubits=3)
        angles = [0.5, 1.0, 1.5]
        fidelity, depth = kernel.evaluate_qiskit(angles, angles, shots=512)
        assert fidelity == 1.0
        assert depth > 0

    def test_qiskit_quantum_kernel_different_fidelity(self):
        kernel = QuantumKernelEngine(num_qubits=2)
        angles_a = [0.0, 0.0]
        angles_b = [np.pi, np.pi]
        fidelity, depth = kernel.evaluate_qiskit(angles_a, angles_b, shots=512)
        assert 0.0 <= fidelity <= 1.0

    def test_pennylane_quantum_kernel(self):
        kernel = QuantumKernelEngine(num_qubits=2)
        angles = [0.8, 1.2]
        fidelity, depth = kernel.evaluate_pennylane(angles, angles, shots=512)
        assert fidelity == 1.0


class TestSimilarityEngine:
    def test_verdict_interpretation(self):
        assert SimilarityEngine.interpret_verdict(0.98) == SimilarityVerdict.IDENTICAL
        assert SimilarityEngine.interpret_verdict(0.80) == SimilarityVerdict.STRONGLY_SIMILAR
        assert SimilarityEngine.interpret_verdict(0.50) == SimilarityVerdict.MODERATELY_SIMILAR
        assert SimilarityEngine.interpret_verdict(0.20) == SimilarityVerdict.DISSIMILAR

    def test_hybrid_similarity_calculation(self):
        hybrid, div = SimilarityEngine.compute_hybrid_similarity(0.80, 0.90)
        assert hybrid == 0.85
        assert div == 0.10


class TestSemanticDatasetAndEvaluator:
    def test_dataset_adapter_load_and_split(self):
        adapter = SemanticDatasetAdapter()
        pairs = adapter.load()
        assert len(pairs) >= 10

        train, test = adapter.split(test_ratio=0.3, seed=42)
        assert len(train) + len(test) == len(pairs)
        assert len(test) >= 2

    def test_evaluator_metrics(self):
        y_true = [1.0, 0.8, 0.5, 0.1]
        y_pred = [0.95, 0.75, 0.45, 0.15]
        mae, rmse, p_r, s_rho = SemanticBenchmarkEvaluator.calculate_metrics(y_true, y_pred)
        assert 0.0 <= mae <= 0.1
        assert 0.0 <= rmse <= 0.1
        assert p_r > 0.9


class TestQuantumSemanticService:
    def test_analyze_similarity_hybrid(self):
        service = QuantumSemanticService()
        req = SemanticAnalysisRequest(
            text_a="Deep learning and artificial intelligence for speech synthesis.",
            text_b="Text to speech algorithms using neural network models.",
            method="hybrid",
            num_qubits=4,
            shots=512,
        )
        res = service.analyze_similarity(req)
        assert res.text_a == req.text_a
        assert res.text_b == req.text_b
        assert 0.0 <= res.quantum_kernel_similarity <= 1.0
        assert 0.0 <= res.classical_cosine_similarity <= 1.0
        assert 0.0 <= res.similarity_score <= 1.0
        assert res.similarity_verdict in [v.value for v in SimilarityVerdict]
        assert res.divergence >= 0.0
        assert res.semantic_distance >= 0.0
        assert res.circuit_depth > 0
        assert res.num_qubits == 4
        assert res.execution_time_ms > 0
        assert len(res.pipeline_steps) > 0

    def test_analyze_similarity_classical_only(self):
        service = QuantumSemanticService()
        req = SemanticAnalysisRequest(
            text_a="Natural speech synthesis audio.",
            text_b="Voice speech synthesis engine.",
            method="classical",
            num_qubits=2,
        )
        res = service.analyze_similarity(req)
        assert res.method == "classical"
        assert res.quantum_similarity is None
        assert res.classical_similarity > 0.0
        assert res.circuit_depth == 0

    def test_compute_matrix_bounded(self):
        service = QuantumSemanticService()
        req = SemanticMatrixRequest(
            texts=[
                "Speech generation platform.",
                "Text to speech synthesis.",
                "Quantum circuit simulation.",
            ],
            method="classical",
            num_qubits=2,
        )
        matrix_res = service.compute_matrix(req)
        assert matrix_res.num_texts == 3
        assert matrix_res.total_comparisons == 3
        assert len(matrix_res.matrix) == 3
        assert len(matrix_res.matrix[0]) == 3
        # Diagonal should be 1.0
        assert matrix_res.matrix[0][0] == 1.0
        assert matrix_res.matrix[1][1] == 1.0
        assert matrix_res.matrix[2][2] == 1.0

    def test_compute_matrix_rejects_excessive_pairs(self):
        service = QuantumSemanticService()
        # 10 texts is 45 pairs which exceeds the 20 pair limit
        req = SemanticMatrixRequest(
            texts=[f"Prompt number {i}" for i in range(8)],  # 8 texts = 28 pairs > 20
            method="classical",
        )
        with pytest.raises(SemanticResourceLimitException):
            service.compute_matrix(req)
