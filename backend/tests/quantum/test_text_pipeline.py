"""
Unit and Component Tests for Quantum Text Intelligence Pipeline
Covers: Text Preprocessing, TF-IDF Vectorization, TruncatedSVD Reduction,
Angle Normalization, Quantum Feature Encoding, Parameterized Circuit Construction,
Hybrid Quantum & Classical Baseline Classifiers, and Leakage-Free Evaluation.
"""

import math
import numpy as np
import pytest
from scipy import sparse

from backend.app.quantum.text import (
    AngleFeatureEncoder,
    ClassicalTextBaselineClassifier,
    FeatureAngleNormalizer,
    FeatureEncodingFailedException,
    HybridQuantumTextClassifier,
    QuantumTextBenchmarkEvaluator,
    QuantumTextInvalidException,
    QuantumTextPreprocessor,
    TextFeatureExtractor,
    TextQuantumCircuitBuilder,
    TruncatedSVDReducer,
)


# ==============================================================================
# 1. Text Preprocessing & Validation Tests
# ==============================================================================
def test_preprocessor_valid_text():
    preprocessor = QuantumTextPreprocessor(max_characters=100)
    cleaned = preprocessor.validate_and_clean("  Quantum NLP with Variational Circuits \r\n ")
    assert cleaned == "Quantum NLP with Variational Circuits"


def test_preprocessor_unicode_nfkc_normalization():
    preprocessor = QuantumTextPreprocessor()
    # Ligature ﬁ (U+FB01) should normalize to "fi" under NFKC
    raw = "The ﬁnal statevector"
    cleaned = preprocessor.validate_and_clean(raw)
    assert cleaned == "The final statevector"


def test_preprocessor_empty_rejection():
    preprocessor = QuantumTextPreprocessor()
    with pytest.raises(QuantumTextInvalidException):
        preprocessor.validate_and_clean("")

    with pytest.raises(QuantumTextInvalidException):
        preprocessor.validate_and_clean("    \t \n  ")

    with pytest.raises(QuantumTextInvalidException):
        preprocessor.validate_and_clean(None)


def test_preprocessor_length_limit():
    preprocessor = QuantumTextPreprocessor(max_characters=15)
    with pytest.raises(QuantumTextInvalidException) as exc_info:
        preprocessor.validate_and_clean("This text is definitely too long for the limit.")
    assert "exceeds maximum allowable" in str(exc_info.value.message)


def test_preprocessor_tokenization():
    preprocessor = QuantumTextPreprocessor()
    tokens = preprocessor.tokenize("Quantum circuit depth: 4 gates, 1024 shots!")
    assert tokens == ["quantum", "circuit", "depth", "4", "gates", "1024", "shots"]


# ==============================================================================
# 2. Classical TF-IDF Feature Extraction Tests
# ==============================================================================
def test_tfidf_feature_extractor_default():
    extractor = TextFeatureExtractor(max_features=16)
    extractor.fit_default()
    assert extractor.is_fitted
    assert len(extractor.vocabulary) <= 16

    vec = extractor.transform("quantum computing variational circuit")
    assert sparse.issparse(vec)
    assert vec.shape == (1, len(extractor.vocabulary))


def test_tfidf_feature_extractor_custom_corpus():
    corpus = [
        "quantum entanglement bell states",
        "classical logistic regression models",
        "hybrid quantum neural network",
    ]
    extractor = TextFeatureExtractor(max_features=8)
    res = extractor.fit_transform(corpus)
    assert res.shape == (3, len(extractor.vocabulary))
    assert extractor.is_fitted


# ==============================================================================
# 3. TruncatedSVD Dimensionality Reduction Tests
# ==============================================================================
def test_truncated_svd_reducer_dimension():
    # 10 samples, 20 features
    rng = np.random.RandomState(42)
    X = sparse.csr_matrix(rng.uniform(0, 1, size=(10, 20)))

    reducer = TruncatedSVDReducer(target_dimension=4, random_state=42)
    reduced = reducer.fit_transform(X)

    assert reducer.is_fitted
    assert reduced.shape == (10, 4)
    assert isinstance(reduced, np.ndarray)


def test_truncated_svd_reducer_padding():
    # When samples are very few, components can be capped and zero-padded to target
    X = sparse.csr_matrix(np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))
    reducer = TruncatedSVDReducer(target_dimension=4, random_state=42)
    reduced = reducer.fit_transform(X)
    assert reduced.shape == (2, 4)


# ==============================================================================
# 4. Feature Angle Normalization & Encoding Tests
# ==============================================================================
def test_feature_angle_normalizer():
    normalizer = FeatureAngleNormalizer(min_angle=0.0, max_angle=math.pi)
    raw = np.array([[-5.0, 0.0, 10.0], [5.0, -2.0, 8.0]])
    angles = normalizer.fit_transform(raw)

    assert np.all(angles >= 0.0)
    assert np.all(angles <= math.pi + 1e-6)


def test_feature_angle_normalizer_rejection_of_nan_inf():
    normalizer = FeatureAngleNormalizer()
    with pytest.raises(FeatureEncodingFailedException):
        normalizer.fit_transform(np.array([[1.0, float("nan")], [0.0, 2.0]]))

    with pytest.raises(FeatureEncodingFailedException):
        normalizer.fit_transform(np.array([[1.0, float("inf")], [0.0, 2.0]]))


def test_angle_feature_encoder():
    encoder = AngleFeatureEncoder(target_qubits=4)
    assert encoder.required_qubits == 4

    features = [0.1, 0.5, 0.9]
    encoded = encoder.encode(features)
    assert len(encoded) == 4
    for a in encoded:
        assert 0.0 <= a <= math.pi + 1e-6


def test_angle_feature_encoder_truncation():
    encoder = AngleFeatureEncoder(target_qubits=3)
    encoded = encoder.encode([1.0, 2.0, 3.0, 4.0, 5.0])
    assert len(encoded) == 3


# ==============================================================================
# 5. Parameterized Circuit Construction Tests
# ==============================================================================
def test_circuit_builder_qiskit():
    builder = TextQuantumCircuitBuilder(num_qubits=4, circuit_depth=2)
    qc, x_params, w_params = builder.build_parameterized_circuit()

    assert qc.num_qubits == 4
    assert len(x_params) == 4
    assert len(w_params) == 8  # 4 qubits * 2 depth

    # Concrete binding
    bound = builder.bind_circuit(features=[0.5, 1.2, 2.1, 0.8])
    assert bound.depth() > 0
    assert bound.num_qubits == 4


# ==============================================================================
# 6. Hybrid & Classical Classifiers Simulation Tests
# ==============================================================================
def test_hybrid_quantum_classifier_qiskit():
    classifier = HybridQuantumTextClassifier(num_qubits=4, circuit_depth=1, shots=512, framework="qiskit")
    pred, conf, probs, depth = classifier.predict([0.1, 0.8, 1.5, 2.2])

    assert pred in ["technical", "formal", "casual", "creative"]
    assert conf is not None and conf > 0.0
    assert isinstance(probs, dict)
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-2)
    assert depth > 0


def test_hybrid_quantum_classifier_pennylane():
    classifier = HybridQuantumTextClassifier(num_qubits=2, circuit_depth=1, shots=512, framework="pennylane")
    pred, conf, probs, depth = classifier.predict([0.5, 1.0])

    assert pred in ["technical", "formal", "casual", "creative"]
    assert conf is not None and conf > 0.0
    assert depth > 0


def test_classical_baseline_classifier():
    classifier = ClassicalTextBaselineClassifier(random_state=42)
    X = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9]])
    y = np.array([0, 0, 1, 1])

    classifier.fit(X, y)
    preds, confs = classifier.predict(np.array([[0.8, 0.2], [0.2, 0.8]]))

    assert len(preds) == 2
    assert preds[0] == 0
    assert preds[1] == 1
    assert confs is not None and len(confs) == 2


# ==============================================================================
# 7. Leakage-Free Benchmark Evaluator Tests
# ==============================================================================
def test_benchmark_evaluator_zero_leakage():
    evaluator = QuantumTextBenchmarkEvaluator(
        num_qubits=2,
        circuit_depth=1,
        shots=256,
        framework="qiskit",
        test_size=0.25,
        random_state=42,
    )

    # Balanced synthetic corpus with distinct semantic domains
    texts = [
        "quantum computing qubit statevector circuit gate",
        "quantum entanglement simulator variational algorithm",
        "quantum teleportation measurement hermitian unitary operator",
        "superconducting qubits ion trap quantum processor",
        "corporate governance compliance institutional executive policy",
        "formal authorization pursuant to administrative guidelines committee",
        "official quarterly financial compliance balance sheet report",
        "regulatory contractual framework binding governance agreement",
    ]
    labels = [0, 0, 0, 0, 1, 1, 1, 1]

    classic_metrics, quantum_metrics, advantage, analysis = evaluator.evaluate_dataset(texts, labels)

    # Verify metrics structure
    assert 0.0 <= classic_metrics.accuracy <= 1.0
    assert 0.0 <= quantum_metrics.accuracy <= 1.0
    assert classic_metrics.f1_score >= 0.0
    assert quantum_metrics.f1_score >= 0.0
    assert isinstance(advantage, bool)
    assert isinstance(analysis, str) and len(analysis) > 20
