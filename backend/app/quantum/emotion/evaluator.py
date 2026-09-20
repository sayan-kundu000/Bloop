"""
Quantum Emotion Intelligence — Benchmark Evaluator
Enforces strict train/test isolation, fits all transformations exclusively on train,
and computes empirical metrics comparing Classical Baseline vs Hybrid QNN.
"""

import time
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from backend.app.quantum.emotion.dataset import EmotionDataset
from backend.app.quantum.emotion.features import EmotionFeatureExtractor
from backend.app.quantum.emotion.reduction import EmotionSVDReducer
from backend.app.quantum.emotion.normalization import EmotionAngleNormalizer
from backend.app.quantum.emotion.classifier import HybridEmotionClassifier, ClassicalEmotionBaseline
from backend.app.quantum.emotion.models import EmotionMetrics


class EmotionBenchmarkEvaluator:
    """
    Evaluates Hybrid QNN vs Classical Baseline with zero data leakage.
    """

    def __init__(self, dataset: EmotionDataset = None, num_qubits: int = 4):
        self.dataset = dataset or EmotionDataset()
        self.num_qubits = num_qubits

    def run_benchmark(self) -> Tuple[EmotionMetrics, Dict[str, Any], HybridEmotionClassifier, ClassicalEmotionBaseline, EmotionFeatureExtractor, EmotionSVDReducer, EmotionAngleNormalizer]:
        """
        Executes strict leakage-free benchmark.
        Transformers are fitted ONLY on training split.
        """
        train_texts = self.dataset.train_texts
        train_labels = self.dataset.train_labels
        test_texts = self.dataset.test_texts
        test_labels = self.dataset.test_labels

        # 1. Pipeline Fitting on Train Split
        extractor = EmotionFeatureExtractor(max_features=32)
        X_train_sparse = extractor.fit_transform(train_texts)
        X_test_sparse = extractor.transform(test_texts)

        reducer = EmotionSVDReducer(target_dim=self.num_qubits)
        X_train_reduced = reducer.fit_transform(X_train_sparse)
        X_test_reduced = reducer.transform(X_test_sparse)

        normalizer = EmotionAngleNormalizer()
        X_train_angles = normalizer.fit_transform(X_train_reduced)
        X_test_angles = normalizer.transform(X_test_reduced)

        # 2. Classical Baseline Evaluation
        classical_model = ClassicalEmotionBaseline()
        start_train_c = time.perf_counter()
        classical_model.fit(X_train_reduced, train_labels)
        train_time_c = time.perf_counter() - start_train_c

        start_pred_c = time.perf_counter()
        y_pred_c = classical_model.model.predict(X_test_reduced)
        pred_time_c = time.perf_counter() - start_pred_c

        acc_c = float(accuracy_score(test_labels, y_pred_c))
        prec_c, rec_c, f1_c, _ = precision_recall_fscore_support(test_labels, y_pred_c, average="weighted", zero_division=0)

        # 3. Hybrid QNN Evaluation
        qnn_classifier = HybridEmotionClassifier()
        start_train_q = time.perf_counter()
        qnn_classifier.fit(X_train_angles, train_labels)
        train_time_q = time.perf_counter() - start_train_q

        start_pred_q = time.perf_counter()
        probas_q = qnn_classifier.predict_proba(X_test_angles)
        pred_time_q = time.perf_counter() - start_pred_q

        y_pred_q = [qnn_classifier.classes_[int(np.argmax(p))] for p in probas_q]

        acc_q = float(accuracy_score(test_labels, y_pred_q))
        prec_q, rec_q, f1_q, _ = precision_recall_fscore_support(test_labels, y_pred_q, average="weighted", zero_division=0)

        q_metrics = EmotionMetrics(
            accuracy=acc_q,
            precision=float(prec_q),
            recall=float(rec_q),
            f1_score=float(f1_q),
            training_time_seconds=train_time_q,
            inference_time_seconds=pred_time_q,
            quantum_execution_time_seconds=pred_time_q,
        )

        c_summary = {
            "model": "logistic_regression",
            "accuracy": round(acc_c, 4),
            "precision": round(float(prec_c), 4),
            "recall": round(float(rec_c), 4),
            "f1_score": round(float(f1_c), 4),
            "training_time_seconds": round(train_time_c, 4),
            "inference_time_seconds": round(pred_time_c, 4),
        }

        return q_metrics, c_summary, qnn_classifier, classical_model, extractor, reducer, normalizer
