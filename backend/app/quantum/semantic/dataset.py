"""
Bloop Semantic Benchmark Dataset Adapter
Provides a reproducible, leakage-free dataset adapter containing curated
reference semantic evaluation pairs across distinct similarity tiers.
"""

from typing import Any, Dict, List, Tuple
import random
from backend.app.quantum.semantic.exceptions import SemanticDatasetInvalidException
from backend.app.quantum.semantic.models import SemanticBenchmarkPair

# Curated reference semantic pairs with human-calibrated similarity scores [0.0, 1.0]
# Across: Identical, Strong Paraphrase, Topical Relation, and Dissimilar.
CURATED_REFERENCE_PAIRS: List[Dict[str, Any]] = [
    # 1. Identical Pairs (1.0)
    {
        "text_a": "Artificial intelligence converts written text into synthetic human speech.",
        "text_b": "Artificial intelligence converts written text into synthetic human speech.",
        "expected_similarity": 1.0,
        "category": "identical",
    },
    {
        "text_a": "Quantum computing utilizes superposition and entanglement to process information.",
        "text_b": "Quantum computing utilizes superposition and entanglement to process information.",
        "expected_similarity": 1.0,
        "category": "identical",
    },
    # 2. Strong Paraphrases (0.75 - 0.90)
    {
        "text_a": "The speech engine synthesizes natural vocal audio from text inputs.",
        "text_b": "Text input is converted into natural sounding voice audio by the synthesis engine.",
        "expected_similarity": 0.85,
        "category": "paraphrase",
    },
    {
        "text_a": "Quantum states are manipulated using rotational quantum logic gates.",
        "text_b": "Parameterized logic gates rotate and transform quantum state vectors in Hilbert space.",
        "expected_similarity": 0.80,
        "category": "paraphrase",
    },
    {
        "text_a": "Deep neural networks learn intricate representations from high-dimensional datasets.",
        "text_b": "Complex multi-layer networks extract hierarchical features from large data collections.",
        "expected_similarity": 0.82,
        "category": "paraphrase",
    },
    # 3. Topical Relations (0.40 - 0.60)
    {
        "text_a": "Text to speech systems modulate acoustic pitch, cadence, and vocal tempo.",
        "text_b": "Digital audio workstations record multichannel music and vocal performances.",
        "expected_similarity": 0.50,
        "category": "topical",
    },
    {
        "text_a": "Qiskit simulates quantum circuits with statevector and unitary backends.",
        "text_b": "PennyLane specializes in automatic differentiation and hybrid quantum neural networks.",
        "expected_similarity": 0.55,
        "category": "topical",
    },
    {
        "text_a": "FastAPI provides asynchronous request handling for cloud microservices.",
        "text_b": "PostgreSQL ensures transactional consistency and relational data storage.",
        "expected_similarity": 0.42,
        "category": "topical",
    },
    # 4. Dissimilar Pairs (0.00 - 0.20)
    {
        "text_a": "Quantum statevector fidelity measures state transition overlap in Hilbert space.",
        "text_b": "The quick brown fox jumps over the lazy sleeping dog in the park.",
        "expected_similarity": 0.05,
        "category": "unrelated",
    },
    {
        "text_a": "Acoustic resonance filters shape vowel formant frequencies in vocal tract modeling.",
        "text_b": "Baking sourdough bread requires flour, water, salt, and wild yeast fermentation.",
        "expected_similarity": 0.02,
        "category": "unrelated",
    },
    {
        "text_a": "PostgreSQL database migrations are managed via Alembic revision scripts.",
        "text_b": "Astronauts aboard the International Space Station conducted spacewalks in orbit.",
        "expected_similarity": 0.04,
        "category": "unrelated",
    },
    {
        "text_a": "Deep learning models require high-performance GPU tensor cores for backpropagation.",
        "text_b": "Vintage vinyl records deliver warm analog acoustic distortion through tube amplifiers.",
        "expected_similarity": 0.15,
        "category": "unrelated",
    },
]


class SemanticDatasetAdapter:
    """
    Standardized dataset adapter for semantic similarity benchmarks.
    Isolates reference datasets and ensures split reproducibility with zero data leakage.
    """

    def __init__(self, raw_pairs: List[Dict[str, Any]] = None):
        self._raw_pairs = raw_pairs if raw_pairs is not None else CURATED_REFERENCE_PAIRS
        self._pairs: List[SemanticBenchmarkPair] = []
        self.load()

    def load(self) -> List[SemanticBenchmarkPair]:
        """Loads and parses raw benchmark pairs into validated domain entities."""
        self._pairs = []
        for item in self._raw_pairs:
            pair = SemanticBenchmarkPair(
                text_a=str(item["text_a"]),
                text_b=str(item["text_b"]),
                expected_similarity=float(item["expected_similarity"]),
                category=str(item.get("category", "general")),
            )
            self._pairs.append(pair)
        self.validate()
        return self._pairs

    def validate(self) -> bool:
        """Validates that all benchmark pairs have non-empty text and bounded expected scores."""
        if not self._pairs:
            raise SemanticDatasetInvalidException("Benchmark dataset is empty.")
        for p in self._pairs:
            if not p.text_a.strip() or not p.text_b.strip():
                raise SemanticDatasetInvalidException("Benchmark pair contains empty text.")
            if not (0.0 <= p.expected_similarity <= 1.0):
                raise SemanticDatasetInvalidException(
                    f"Expected similarity {p.expected_similarity} outside [0.0, 1.0]."
                )
        return True

    def split(self, test_ratio: float = 0.25, seed: int = 42) -> Tuple[List[SemanticBenchmarkPair], List[SemanticBenchmarkPair]]:
        """
        Splits dataset into train/reference and test sets.
        Splitting occurs before any feature or reduction transformations.
        """
        self.validate()
        pairs = list(self._pairs)
        rng = random.Random(seed)
        rng.shuffle(pairs)

        test_count = max(1, int(len(pairs) * test_ratio))
        test_set = pairs[:test_count]
        train_set = pairs[test_count:]
        return train_set, test_set

    def metadata(self) -> Dict[str, Any]:
        """Returns provenance and licensing metadata for the benchmark dataset."""
        return {
            "dataset_name": "BSEB-v1 (Bloop Semantic Evaluation Benchmark)",
            "sample_count": len(self._pairs),
            "categories": list(set(p.category for p in self._pairs)),
            "licensing": "MIT / Open Scientific Research",
            "task": "Pairwise Text Semantic Similarity Estimation",
            "ground_truth_scale": "[0.0, 1.0] (0.0 = completely unrelated, 1.0 = identical)",
        }
