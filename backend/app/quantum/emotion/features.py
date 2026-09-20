"""
Quantum Emotion Intelligence — Affective Feature Extractor
Extracts deterministic lexical (TF-IDF) and statistical signals from normalized text.
Maintains strict train/test isolation to prevent data leakage.
"""

import math
import re
from typing import List, Optional
import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.app.quantum.emotion.exceptions import EmotionFeatureExtractionFailedException
from backend.app.quantum.emotion.labels import EmotionLabel

# Deterministic affective valence reference lexicons for signal extraction
AFfECTIVE_LEXICON = {
    EmotionLabel.JOY.value: [
        "happy", "delighted", "love", "great", "wonderful", "joy", "joyful",
        "excited", "fantastic", "smile", "laugh", "glad", "superb", "brilliant", "cheerful"
    ],
    EmotionLabel.SADNESS.value: [
        "sad", "depressed", "sorrow", "grief", "pain", "unhappy", "cry",
        "lonely", "tears", "loss", "mourn", "hurt", "terrible", "gloomy"
    ],
    EmotionLabel.ANGER.value: [
        "angry", "rage", "furious", "hate", "mad", "annoyed", "irritated",
        "hostile", "outraged", "bitter", "fuming", "spite", "resent"
    ],
    EmotionLabel.NEUTRAL.value: [
        "is", "the", "system", "file", "text", "audio", "data", "status",
        "process", "ready", "input", "standard", "application", "normal"
    ],
}


class EmotionFeatureExtractor:
    """
    Extracts high-dimensional classical emotion features from text.
    Combines vocabulary-bounded TF-IDF with deterministic statistical affective signals.
    """

    def __init__(self, max_features: int = 32):
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            token_pattern=r"(?u)\b\w+\b",
            sublinear_tf=True,
            norm="l2",
        )
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    def _extract_statistical_features(self, texts: List[str]) -> np.ndarray:
        """
        Computes deterministic affective statistics:
        [exclamation_density, question_density, uppercase_ratio, joy_lex, sadness_lex, anger_lex, neutral_lex]
        """
        stats_list = []
        for text in texts:
            total_chars = max(len(text), 1)
            words = re.findall(r"\b\w+\b", text)
            total_words = max(len(words), 1)

            # Exclamation & question density
            excl_density = text.count("!") / total_words
            quest_density = text.count("?") / total_words

            # Uppercase word ratio (intensity signal)
            upper_words = sum(1 for w in words if w.isupper() and len(w) > 1)
            upper_ratio = upper_words / total_words

            # Lexicon valence match counts normalized by total words
            text_lower = text.lower()
            tokens_lower = set(re.findall(r"\b\w+\b", text_lower))

            joy_matches = sum(1 for w in AFfECTIVE_LEXICON[EmotionLabel.JOY.value] if w in tokens_lower)
            sad_matches = sum(1 for w in AFfECTIVE_LEXICON[EmotionLabel.SADNESS.value] if w in tokens_lower)
            ang_matches = sum(1 for w in AFfECTIVE_LEXICON[EmotionLabel.ANGER.value] if w in tokens_lower)
            neu_matches = sum(1 for w in AFfECTIVE_LEXICON[EmotionLabel.NEUTRAL.value] if w in tokens_lower)

            row = [
                min(excl_density, 3.0) / 3.0,
                min(quest_density, 3.0) / 3.0,
                upper_ratio,
                joy_matches / 5.0,
                sad_matches / 5.0,
                ang_matches / 5.0,
                neu_matches / 5.0,
            ]
            stats_list.append(row)

        return np.array(stats_list, dtype=np.float64)

    def fit(self, texts: List[str]) -> "EmotionFeatureExtractor":
        """
        Fits the TF-IDF vectorizer exclusively on training texts.
        """
        try:
            self.vectorizer.fit(texts)
            self._is_fitted = True
            return self
        except Exception as e:
            raise EmotionFeatureExtractionFailedException(
                f"Failed to fit emotion feature extractor: {str(e)}"
            )

    def transform(self, texts: List[str]) -> csr_matrix:
        """
        Transforms input texts into combined sparse feature matrix (TF-IDF + statistical signals).
        """
        if not self._is_fitted:
            raise EmotionFeatureExtractionFailedException(
                "EmotionFeatureExtractor must be fitted before transforming texts."
            )

        try:
            tfidf_mat = self.vectorizer.transform(texts)
            stats_mat = csr_matrix(self._extract_statistical_features(texts))
            combined = hstack([tfidf_mat, stats_mat], format="csr")
            return combined
        except Exception as e:
            raise EmotionFeatureExtractionFailedException(
                f"Failed to transform texts into emotion feature matrix: {str(e)}"
            )

    def fit_transform(self, texts: List[str]) -> csr_matrix:
        """
        Fits and transforms strictly in one step for training splits.
        """
        self.fit(texts)
        return self.transform(texts)
