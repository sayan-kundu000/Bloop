import numpy as np
import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA


# Baseline reference vocabulary corpus for reliable vectorization across diverse text
REFERENCE_CORPUS = [
    "welcome to the modern speech synthesis and audio generation platform",
    "advanced artificial intelligence and deep neural network models",
    "quantum computing variational circuits and statevector simulations",
    "natural language processing semantic text analysis and sentiment",
    "high performance cloud microservices backend rest api architecture",
    "the quick brown fox jumps over the lazy dog in the sunny park",
    "joyful wonderful cheerful happy ecstatic delightful experience",
    "terrible sorrowful painful grief melancholic sad depressing feeling",
    "furious outraged irritable hostile aggressive hateful behavior",
    "formal executive professional corporate official academic documentation",
    "casual friendly conversational everyday chat dialogue discussion",
    "technical algorithmic mathematical scientific scientific computation logic",
    "poetic imaginative creative artistic expressive vivid imagery",
]


class TextFeatureExtractor:
    """
    Extracts numerical features from raw text and projects them
    into angles suitable for quantum state encoding (angle encoding in [0, pi]).
    """

    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits
        self.vectorizer = TfidfVectorizer(max_features=64, stop_words="english")
        # Fit on baseline reference corpus
        self.vectorizer.fit(REFERENCE_CORPUS)

    def extract_features(self, text: str) -> np.ndarray:
        cleaned = re.sub(r"[^\w\s]", "", text.lower()).strip()
        vec = self.vectorizer.transform([cleaned]).toarray()[0]

        # Use PCA or deterministic projection to reduce to num_qubits dimensions
        if len(vec) < self.num_qubits:
            padded = np.zeros(self.num_qubits)
            padded[:len(vec)] = vec
            features = padded
        else:
            # Deterministic chunk pooling to preserve signal
            chunk_size = len(vec) // self.num_qubits
            features = np.zeros(self.num_qubits)
            for i in range(self.num_qubits):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i < self.num_qubits - 1 else len(vec)
                features[i] = np.mean(vec[start:end]) if end > start else 0.0

        # Normalize features to [0, pi] for rotational gate angles (Rx, Ry)
        norm = np.linalg.norm(features)
        if norm > 1e-6:
            features = features / norm
        angles = np.pi * (0.5 * (features + 1.0) % 1.0)
        return angles

    def tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())
