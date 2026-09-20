"""
Bloop Quantum Text Experiment Evaluator
Evaluates hybrid quantum classifiers against classical baselines with strict
train/test split separation, preventing data leakage at every pipeline stage.
"""

import time
from typing import List, Tuple
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from backend.app.quantum.text.classifier import (
    ClassicalTextBaselineClassifier,
    HybridQuantumTextClassifier,
)
from backend.app.quantum.text.encoder import AngleFeatureEncoder
from backend.app.quantum.text.exceptions import DatasetInvalidException
from backend.app.quantum.text.features import TextFeatureExtractor
from backend.app.quantum.text.models import ClassificationMetrics
from backend.app.quantum.text.normalization import FeatureAngleNormalizer
from backend.app.quantum.text.reduction import TruncatedSVDReducer


class QuantumTextBenchmarkEvaluator:
    """
    Executes rigorous, leakage-free benchmark experiments comparing Classical Logistic
    Regression against Hybrid Quantum Classifiers on text corpora.
    """

    def __init__(
        self,
        num_qubits: int = 4,
        circuit_depth: int = 2,
        shots: int = 1024,
        framework: str = "qiskit",
        test_size: float = 0.25,
        random_state: int = 42,
    ):
        self.num_qubits = max(2, min(num_qubits, 8))
        self.circuit_depth = circuit_depth
        self.shots = shots
        self.framework = framework
        self.test_size = test_size
        self.random_state = random_state

    def evaluate_dataset(
        self,
        texts: List[str],
        labels: List[int],
    ) -> Tuple[ClassificationMetrics, ClassificationMetrics, bool, str]:
        """
        Executes end-to-end benchmark with ZERO data leakage:
        1. Split texts and labels into Train and Test splits.
        2. Fit TF-IDF, TruncatedSVD, and Normalizer ONLY on Train split.
        3. Transform Test split using fitted transformers.
        4. Train and test Classical Baseline.
        5. Train and test Hybrid Quantum Model.
        6. Compute metrics and un-doctored comparison.
        """
        if len(texts) != len(labels):
            raise DatasetInvalidException("Text samples count must equal labels count.")
        if len(texts) < 8:
            raise DatasetInvalidException("Benchmark requires at least 8 samples for stratified train/test split.")

        unique_labels = list(set(labels))
        if len(unique_labels) < 2:
            raise DatasetInvalidException("Benchmark requires at least 2 distinct classes.")

        # 1. Strict Train / Test Split FIRST
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            texts,
            labels,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=labels,
        )

        # 2. Fit feature transformations ONLY on train split
        extractor = TextFeatureExtractor(max_features=64)
        X_train_tfidf = extractor.fit_transform(X_train_raw)
        X_test_tfidf = extractor.transform(X_test_raw)

        # Fit TruncatedSVD ONLY on train
        reducer = TruncatedSVDReducer(target_dimension=self.num_qubits, random_state=self.random_state)
        X_train_reduced = reducer.fit_transform(X_train_tfidf)
        X_test_reduced = reducer.transform(X_test_tfidf)

        # Fit normalizer ONLY on train
        normalizer = FeatureAngleNormalizer()
        X_train_angles = normalizer.fit_transform(X_train_reduced)
        X_test_angles = normalizer.transform(X_test_reduced)

        # 3. Classical Baseline Evaluation
        t0_c_train = time.perf_counter()
        classical = ClassicalTextBaselineClassifier(random_state=self.random_state)
        classical.fit(X_train_reduced, np.array(y_train))
        t_c_train = time.perf_counter() - t0_c_train

        t0_c_pred = time.perf_counter()
        y_pred_c, _ = classical.predict(X_test_reduced)
        t_c_pred = time.perf_counter() - t0_c_pred

        classical_metrics = ClassificationMetrics(
            accuracy=round(float(accuracy_score(y_test, y_pred_c)), 4),
            precision=round(float(precision_score(y_test, y_pred_c, average="weighted", zero_division=0)), 4),
            recall=round(float(recall_score(y_test, y_pred_c, average="weighted", zero_division=0)), 4),
            f1_score=round(float(f1_score(y_test, y_pred_c, average="weighted", zero_division=0)), 4),
            training_time_seconds=round(t_c_train, 4),
            prediction_time_seconds=round(t_c_pred, 4),
        )

        # 4. Quantum Hybrid Classifier Evaluation
        quantum_classifier = HybridQuantumTextClassifier(
            num_qubits=self.num_qubits,
            circuit_depth=self.circuit_depth,
            shots=self.shots,
            framework=self.framework,
            random_state=self.random_state,
        )

        t0_q_train = time.perf_counter()
        quantum_classifier.fit(X_train_angles, np.array(y_train))
        t_q_train = time.perf_counter() - t0_q_train

        t0_q_pred = time.perf_counter()
        y_pred_q = []
        for row in X_test_angles:
            pred, _, _, _ = quantum_classifier.predict(row.tolist())
            y_pred_q.append(pred)
        t_q_pred = time.perf_counter() - t0_q_pred

        quantum_metrics = ClassificationMetrics(
            accuracy=round(float(accuracy_score(y_test, y_pred_q)), 4),
            precision=round(float(precision_score(y_test, y_pred_q, average="weighted", zero_division=0)), 4),
            recall=round(float(recall_score(y_test, y_pred_q, average="weighted", zero_division=0)), 4),
            f1_score=round(float(f1_score(y_test, y_pred_q, average="weighted", zero_division=0)), 4),
            training_time_seconds=round(t_q_train, 4),
            prediction_time_seconds=round(t_q_pred, 4),
            quantum_execution_time_seconds=round(t_q_train + t_q_pred, 4),
        )

        # 5. Scientific, Un-doctored Analysis
        advantage = bool(
            quantum_metrics.accuracy > classical_metrics.accuracy
            and quantum_metrics.f1_score > classical_metrics.f1_score
        )

        if advantage:
            analysis = (
                f"Quantum hybrid classifier achieved superior test accuracy ({quantum_metrics.accuracy}) and F1 ({quantum_metrics.f1_score}) "
                f"compared to classical baseline ({classical_metrics.accuracy} acc, {classical_metrics.f1_score} F1). "
                f"Classical inference remained faster ({classical_metrics.prediction_time_seconds}s vs {quantum_metrics.prediction_time_seconds}s)."
            )
        else:
            analysis = (
                f"Classical baseline matched or exceeded hybrid quantum model "
                f"(Classical: {classical_metrics.accuracy} acc, {classical_metrics.f1_score} F1; "
                f"Quantum: {quantum_metrics.accuracy} acc, {quantum_metrics.f1_score} F1). "
                f"As expected on small simulated benchmark corpora, classical models provide lower latency and superior numerical stability."
            )

        return classical_metrics, quantum_metrics, advantage, analysis
