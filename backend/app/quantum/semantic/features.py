"""
Bloop Quantum Semantic Intelligence Feature Representation
Implements transparent classical semantic representations including TF-IDF
and deterministic lexical feature providers behind a clean provider abstraction.
"""

from abc import ABC, abstractmethod
import math
import re
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.app.quantum.semantic.exceptions import SemanticFeatureExtractionFailedException

# Robust reference corpus representing diverse speech synthesis, artificial intelligence,
# computing, emotional states, and communication domains for fitting vocabulary.
REFERENCE_SEMANTIC_CORPUS = [
    "welcome to modern speech synthesis and text to speech audio generation",
    "advanced artificial intelligence deep learning neural network computational models",
    "quantum computing variational circuits statevector simulation and qubit registers",
    "natural language processing semantic text analysis similarity and lexical representation",
    "high performance cloud microservices backend rest api fast api architecture",
    "the quick brown fox jumps over the lazy dog in the sunny park",
    "joyful wonderful cheerful happy ecstatic delightful emotional experience",
    "terrible sorrowful painful grief melancholic sad depressing emotional feeling",
    "furious outraged irritable hostile aggressive hateful behavior and anger",
    "formal executive professional corporate official academic documentation",
    "casual friendly conversational everyday chat dialogue discussion",
    "technical algorithmic mathematical scientific computation and logical reasoning",
    "creative poetic imaginative artistic expressive vivid imagery and narrative",
    "information processing data structures algorithms memory management latency",
    "voice modulation acoustic pitch cadence resonance tempo timbre filter",
]


class SemanticRepresentationProvider(ABC):
    """Abstract base provider for semantic text representation."""

    @abstractmethod
    def extract_features(self, text: str) -> np.ndarray:
        """Transforms raw cleaned text into a 1D numerical feature vector."""
        pass

    @property
    @abstractmethod
    def feature_dimension(self) -> int:
        """Returns the output feature vector dimension."""
        pass

    @property
    @abstractmethod
    def representation_name(self) -> str:
        """Returns human-readable representation name."""
        pass


class TfidfFeatureProvider(SemanticRepresentationProvider):
    """
    Classical TF-IDF Semantic Feature Representation.
    Note: TF-IDF is a bag-of-words lexical statistic, NOT a deep contextual neural embedding.
    """

    def __init__(self, max_features: int = 64):
        self._max_features = max(16, min(max_features, 128))
        self.vectorizer = TfidfVectorizer(
            max_features=self._max_features,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        try:
            self.vectorizer.fit(REFERENCE_SEMANTIC_CORPUS)
        except Exception as e:
            raise SemanticFeatureExtractionFailedException(
                f"Failed to fit reference TF-IDF vocabulary: {e}"
            )

    @property
    def feature_dimension(self) -> int:
        return len(self.vectorizer.get_feature_names_out())

    @property
    def representation_name(self) -> str:
        return "TF-IDF (Sublinear Term Frequency-Inverse Document Frequency)"

    def extract_features(self, text: str) -> np.ndarray:
        try:
            cleaned = re.sub(r"[^\w\s]", "", text.lower()).strip()
            if not cleaned:
                return np.zeros(self.feature_dimension, dtype=float)
            vec = self.vectorizer.transform([cleaned]).toarray()[0]
            return vec.astype(float)
        except Exception as e:
            raise SemanticFeatureExtractionFailedException(
                f"TF-IDF feature extraction failed: {e}",
                details={"text_preview": text[:50]},
            )


class LexicalFeatureProvider(SemanticRepresentationProvider):
    """
    Deterministic Handcrafted Lexical Semantic Representation.
    Extracts deterministic surface, syntactic, and character n-gram statistics.
    """

    def __init__(self, feature_dim: int = 16):
        self._feature_dim = max(8, min(feature_dim, 32))

    @property
    def feature_dimension(self) -> int:
        return self._feature_dim

    @property
    def representation_name(self) -> str:
        return "Deterministic Handcrafted Lexical Features"

    def extract_features(self, text: str) -> np.ndarray:
        try:
            features = np.zeros(self._feature_dim, dtype=float)
            tokens = re.findall(r"\b\w+\b", text.lower())
            chars = [c for c in text.lower() if not c.isspace()]

            if not tokens or not chars:
                return features

            # 1. Length features
            features[0] = min(1.0, len(chars) / 300.0)
            features[1] = min(1.0, len(tokens) / 50.0)
            features[2] = min(1.0, np.mean([len(t) for t in tokens]) / 12.0)

            # 2. Lexical diversity
            unique_tokens = len(set(tokens))
            features[3] = unique_tokens / len(tokens) if tokens else 0.0

            # 3. Punctuation signals
            features[4] = min(1.0, text.count("?") / 5.0)
            features[5] = min(1.0, text.count("!") / 5.0)
            features[6] = min(1.0, text.count(",") / 10.0)
            features[7] = min(1.0, text.count(".") / 10.0)

            # 4. Character distribution buckets
            for i, token in enumerate(tokens[: self._feature_dim - 8]):
                hash_val = sum(ord(c) for c in token) % 1000 / 1000.0
                idx = 8 + (i % (self._feature_dim - 8))
                features[idx] = (features[idx] + hash_val) / 2.0

            return features
        except Exception as e:
            raise SemanticFeatureExtractionFailedException(
                f"Lexical feature extraction failed: {e}",
                details={"text_preview": text[:50]},
            )


class SemanticFeatureExtractor:
    """Facade orchestrating semantic feature extraction with provider selection."""

    def __init__(self, provider: SemanticRepresentationProvider = None, max_features: int = 64):
        self.provider = provider or TfidfFeatureProvider(max_features=max_features)

    def extract_pair(self, text_a: str, text_b: str) -> Tuple[np.ndarray, np.ndarray]:
        vec_a = self.provider.extract_features(text_a)
        vec_b = self.provider.extract_features(text_b)
        return vec_a, vec_b

    @property
    def feature_dimension(self) -> int:
        return self.provider.feature_dimension

    @property
    def representation_name(self) -> str:
        return self.provider.representation_name
