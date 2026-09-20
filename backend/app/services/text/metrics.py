"""
Bloop Text Processing & Metrics Domain
Defines the canonical data model for calculated text metrics.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass(frozen=True)
class TextMetrics:
    """
    Immutable representation of calculated text metrics for synthesis.
    Contains authoritative character and word counts derived after normalization.
    """
    character_count: int
    word_count: int
    normalized_text: str
    estimated_duration_seconds: float
    speaking_rate_wpm: float = 150.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes metrics to a standard dictionary representation."""
        return asdict(self)

    @property
    def is_empty(self) -> bool:
        """Returns True if the character count is zero."""
        return self.character_count == 0
