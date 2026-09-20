"""
Bloop Classical Text Feature Extraction
Provides TF-IDF vectorization with configurable vocabulary limits.
Maintains strict separation between fitting and transformation to prevent data leakage.
"""

from typing import List, Optional, Union
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.app.quantum.text.exceptions import TextFeatureExtractionFailedException

# Calibrated domain reference corpus covering distinct registers:
# technical, formal, casual, and creative/expressive language.
DEFAULT_REFERENCE_CORPUS = [
    # Technical / Algorithmic
    "quantum computing circuit statevector variational algorithms simulation logic parameters matrix",
    "cloud microservices backend rest api architecture database query execution concurrency latency",
    "deep neural networks machine learning gradient descent backpropagation tensor optimization",
    "software engineering system programming compilation unit testing static analysis",
    # Formal / Corporate / Academic
    "pursuant to executive corporate guidelines hereby submitted for formal official documentation",
    "the committee hereby acknowledges receipt of the quarterly governance report and compliance review",
    "in accordance with contractual obligations and institutional policy we request formal authorization",
    "respectful professional correspondence regarding operational compliance and administrative review",
    # Casual / Conversational
    "hey friend what is up yeah that is pretty cool awesome fun chat catch up later",
    "totally love hanging out and having a relaxed conversation with the team today",
    "yo buddy thanks for checking in let us grab coffee and talk about random things",
    "super excited about the weekend vibes and relaxing with friends after a long week",
    # Creative / Poetic / Vivid
    "crimson sunset dancing across crystalline ocean waves bathed in radiant golden twilight",
    "melodic whispers of ancient autumn winds dancing through shadowy emerald forests",
    "sparkling starlight illuminating silent starry cosmos and mysterious glowing constellations",
    "vivid dreams painted with surreal brushstrokes of wonder and passionate imagination",
]


class TextFeatureExtractor:
    """
    Extracts classical TF-IDF numerical representations from text.
    Can be fitted on arbitrary corpora or initialized with the calibrated domain baseline.
    """

    def __init__(self, max_features: int = 64, stop_words: str = "english"):
        self.max_features = max_features
        self.stop_words = stop_words
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words=self.stop_words,
            sublinear_tf=True,
        )
        self.is_fitted = False

    def fit(self, corpus: List[str]) -> "TextFeatureExtractor":
        """Fits vocabulary exclusively on the provided training corpus."""
        try:
            if not corpus:
                raise ValueError("Corpus for feature extraction cannot be empty.")
            self.vectorizer.fit(corpus)
            self.is_fitted = True
            return self
        except Exception as e:
            raise TextFeatureExtractionFailedException(
                f"Failed to fit TF-IDF vectorizer: {e}",
                details={"corpus_size": len(corpus)},
            )

    def fit_default(self) -> "TextFeatureExtractor":
        """Fits on the reference corpus for standalone prompt inference."""
        return self.fit(DEFAULT_REFERENCE_CORPUS)

    def transform(self, texts: Union[str, List[str]]) -> sparse.spmatrix:
        """
        Transforms input text(s) into sparse TF-IDF feature representations.
        Does NOT update or alter vocabulary.
        """
        if not self.is_fitted:
            self.fit_default()

        if isinstance(texts, str):
            input_list = [texts]
        else:
            input_list = texts

        try:
            return self.vectorizer.transform(input_list)
        except Exception as e:
            raise TextFeatureExtractionFailedException(f"Failed to transform text features: {e}")

    def fit_transform(self, corpus: List[str]) -> sparse.spmatrix:
        """Fits vocabulary and transforms training corpus in a single pass."""
        self.fit(corpus)
        return self.transform(corpus)

    @property
    def vocabulary(self) -> List[str]:
        if not self.is_fitted or not hasattr(self.vectorizer, "vocabulary_") or not self.vectorizer.vocabulary_:
            return []
        return sorted(self.vectorizer.vocabulary_.keys(), key=lambda k: self.vectorizer.vocabulary_[k])
