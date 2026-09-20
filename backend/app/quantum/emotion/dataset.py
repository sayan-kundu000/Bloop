"""
Quantum Emotion Intelligence — Reference Dataset Abstraction
Provides a curated, balanced affective reference corpus for experimentation,
leakage-free train/test splitting, and empirical benchmarking.
"""

from typing import List, Tuple
from sklearn.model_selection import train_test_split
from backend.app.quantum.emotion.labels import EmotionLabel

# Curated reference corpus of clear affective texts across 4 discrete categories
DEFAULT_AFFECTIVE_CORPUS: List[Tuple[str, str]] = [
    # JOY
    ("I am so thrilled and absolutely delighted with this amazing breakthrough!", EmotionLabel.JOY.value),
    ("We celebrated our tremendous success with wonderful joy and happiness.", EmotionLabel.JOY.value),
    ("The fantastic performance brought smiles and cheerful laughter to everyone.", EmotionLabel.JOY.value),
    ("I love this exciting new capability and feel grateful for such great news.", EmotionLabel.JOY.value),
    ("What a superb and brilliant achievement, I am genuinely excited!", EmotionLabel.JOY.value),
    ("The beautiful sunny morning filled our hearts with immense gladness.", EmotionLabel.JOY.value),
    ("Everything turned out wonderfully and the team is completely ecstatic.", EmotionLabel.JOY.value),
    ("This victory is a joyful moment that brings immense optimism.", EmotionLabel.JOY.value),
    ("Hearing your laughter and kind words makes me feel so happy.", EmotionLabel.JOY.value),
    ("We achieved a marvelous milestone that deserves joyful celebration.", EmotionLabel.JOY.value),

    # SADNESS
    ("I feel deeply depressed and overwhelmed by sorrow and painful loss.", EmotionLabel.SADNESS.value),
    ("The tragic news brought heavy grief and lonely tears to all of us.", EmotionLabel.SADNESS.value),
    ("It is heartbreaking to mourn the terrible loss of our dear friend.", EmotionLabel.SADNESS.value),
    ("A gloomy feeling of loneliness and unhappiness surrounds this quiet day.", EmotionLabel.SADNESS.value),
    ("The sorrowful memory hurts and leaves an ache of profound despair.", EmotionLabel.SADNESS.value),
    ("We cried quietly in sadness over the unfortunate turn of events.", EmotionLabel.SADNESS.value),
    ("Everything feels hopeless, cold, and terribly melancholic today.", EmotionLabel.SADNESS.value),
    ("The grief is difficult to bear and the solitude feels unbearable.", EmotionLabel.SADNESS.value),
    ("An agonizing sadness fills the air after the disappointing result.", EmotionLabel.SADNESS.value),
    ("She wept silently in the corner, overwhelmed by sadness and sorrow.", EmotionLabel.SADNESS.value),

    # ANGER
    ("I am furious and absolutely outraged by this unacceptable betrayal!", EmotionLabel.ANGER.value),
    ("This insulting behavior makes me boil with intense rage and anger.", EmotionLabel.ANGER.value),
    ("Stop this hostile harassment immediately, I am extremely annoyed and mad!", EmotionLabel.ANGER.value),
    ("The unfair treatment provoked bitter resentment and fuming indignation.", EmotionLabel.ANGER.value),
    ("I despise this negligence and will not tolerate such spiteful incompetence.", EmotionLabel.ANGER.value),
    ("His rude and offensive remarks provoked furious outrage across the room.", EmotionLabel.ANGER.value),
    ("The irritating violation provoked genuine wrath and deep disgust.", EmotionLabel.ANGER.value),
    ("I am mad that our legitimate concerns were ignored with arrogant spite.", EmotionLabel.ANGER.value),
    ("The hostile confrontation sparked fuming arguments and bitter anger.", EmotionLabel.ANGER.value),
    ("She shouted in complete fury at the disgraceful breach of trust.", EmotionLabel.ANGER.value),

    # NEUTRAL
    ("The system process initialized the audio streaming pipeline normally.", EmotionLabel.NEUTRAL.value),
    ("Please verify the configuration file settings before submitting the data.", EmotionLabel.NEUTRAL.value),
    ("The application completed the standard database synchronization task.", EmotionLabel.NEUTRAL.value),
    ("Output records are stored in the local cache according to specification.", EmotionLabel.NEUTRAL.value),
    ("The input buffer size is configured to four kilobytes by default.", EmotionLabel.NEUTRAL.value),
    ("Network latency metrics were recorded during the scheduled routine inspection.", EmotionLabel.NEUTRAL.value),
    ("Review the documentation guide for information regarding API endpoints.", EmotionLabel.NEUTRAL.value),
    ("The scheduled backup completed successfully without any anomalous events.", EmotionLabel.NEUTRAL.value),
    ("Temperature readings and server telemetry remain within nominal thresholds.", EmotionLabel.NEUTRAL.value),
    ("The report contains factual descriptions of system performance parameters.", EmotionLabel.NEUTRAL.value),
]


class EmotionDataset:
    """
    Manages loading, validation, and leakage-free splitting of emotion reference corpora.
    """

    def __init__(self, corpus: List[Tuple[str, str]] = None, test_size: float = 0.25, random_state: int = 42):
        self.corpus = corpus or DEFAULT_AFFECTIVE_CORPUS
        self.test_size = test_size
        self.random_state = random_state

        self.texts = [item[0] for item in self.corpus]
        self.labels = [item[1] for item in self.corpus]

        # Perform split strictly upon initialization
        self.train_texts, self.test_texts, self.train_labels, self.test_labels = train_test_split(
            self.texts,
            self.labels,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=self.labels,
        )

    @property
    def num_samples(self) -> int:
        return len(self.corpus)

    @property
    def classes(self) -> List[str]:
        return sorted(list(set(self.labels)))
