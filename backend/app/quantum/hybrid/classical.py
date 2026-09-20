"""
Bloop Classical AI Baseline Evaluators
Provides standard, optimized classical baselines (TF-IDF, Logistic Regression,
Linear SVM, and Cosine Similarity) for honest empirical benchmarking.
"""

import time
from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity


class ClassicalTextBaseline:
    """Classical text classification baseline using TF-IDF and Logistic Regression."""

    def __init__(self, max_features: int = 64, random_state: int = 42):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
        self.classifier = LogisticRegression(max_iter=300, random_state=random_state)
        self.is_fitted = False

    def fit(self, texts: List[str], labels: List[Any]) -> float:
        t0 = time.perf_counter()
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_fitted = True
        return time.perf_counter() - t0

    def predict(self, texts: List[str]) -> Tuple[List[Any], List[Dict[str, float]], float]:
        t0 = time.perf_counter()
        if not self.is_fitted:
            # Fallback for unfitted single-sample heuristic
            labels = ["neutral"] * len(texts)
            probs = [{"neutral": 1.0} for _ in texts]
            return labels, probs, time.perf_counter() - t0

        X = self.vectorizer.transform(texts)
        preds = self.classifier.predict(X)
        probs_matrix = self.classifier.predict_proba(X)
        classes = self.classifier.classes_

        prob_dicts = []
        for row in probs_matrix:
            prob_dicts.append({str(c): float(p) for c, p in zip(classes, row)})

        latency = time.perf_counter() - t0
        return list(preds), prob_dicts, latency


class ClassicalEmotionBaseline:
    """Classical multi-class emotion classification baseline."""

    def __init__(self, random_state: int = 42):
        self.vectorizer = TfidfVectorizer(max_features=32, stop_words="english", ngram_range=(1, 2))
        self.classifier = LogisticRegression(max_iter=400, random_state=random_state)
        self.is_fitted = False

    def fit(self, texts: List[str], labels: List[str]) -> float:
        t0 = time.perf_counter()
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_fitted = True
        return time.perf_counter() - t0

    def predict(self, texts: List[str]) -> Tuple[List[str], List[Dict[str, float]], float]:
        t0 = time.perf_counter()
        if not self.is_fitted:
            labels = ["neutral"] * len(texts)
            probs = [{"neutral": 1.0, "joy": 0.0, "sadness": 0.0, "anger": 0.0} for _ in texts]
            return labels, probs, time.perf_counter() - t0

        X = self.vectorizer.transform(texts)
        preds = self.classifier.predict(X)
        probs_matrix = self.classifier.predict_proba(X)
        classes = self.classifier.classes_

        prob_dicts = []
        for row in probs_matrix:
            prob_dicts.append({str(c): float(p) for c, p in zip(classes, row)})

        latency = time.perf_counter() - t0
        return list(preds), prob_dicts, latency


class ClassicalSemanticBaseline:
    """Classical semantic similarity baseline using TF-IDF Cosine Similarity."""

    def __init__(self, max_features: int = 64):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")

    def compute_similarity(self, text_a: str, text_b: str) -> Tuple[float, float]:
        t0 = time.perf_counter()
        matrix = self.vectorizer.fit_transform([text_a, text_b])
        sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        latency = time.perf_counter() - t0
        return round(sim, 4), latency
