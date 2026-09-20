"""
Unit Tests — Text Processor & Pure Functions
Validates character counting, word counting, line-ending normalization,
and control character filtering across standard and edge-case inputs.
"""

import pytest
from backend.app.services.text.processor import (
    TextProcessor,
    count_characters,
    count_words,
    normalize_text,
)


class TestTextNormalization:
    """Tests conservative text normalization behaviors (Prompt 10 §13, §14, §41)."""

    def test_empty_and_none_normalization(self):
        assert normalize_text("") == ""
        assert normalize_text(None) == ""
        assert normalize_text("   ") == ""
        assert normalize_text("\t\t\n  \r\n") == ""

    def test_line_ending_unification(self):
        # Windows CRLF
        assert normalize_text("Hello\r\nWorld") == "Hello\nWorld"
        # Legacy Mac CR
        assert normalize_text("Hello\rWorld") == "Hello\nWorld"
        # Mixed line endings
        assert normalize_text("Line 1\r\nLine 2\rLine 3\nLine 4") == "Line 1\nLine 2\nLine 3\nLine 4"

    def test_surrounding_whitespace_stripping(self):
        assert normalize_text("   Leading and trailing   ") == "Leading and trailing"
        assert normalize_text("\n\nParagraph text\n\n") == "Paragraph text"
        assert normalize_text("\t\tIndented text\t\t") == "Indented text"

    def test_preserves_internal_structural_whitespace(self):
        # Multiple spaces inside text must be preserved faithfully
        assert normalize_text("Word1   Word2") == "Word1   Word2"
        # Paragraph double newlines must be preserved
        assert normalize_text("Paragraph 1\n\nParagraph 2") == "Paragraph 1\n\nParagraph 2"
        # Internal tabs preserved
        assert normalize_text("Col1\tCol2") == "Col1\tCol2"

    def test_control_character_sanitization(self):
        # Null bytes (\x00), bells (\x07), backspaces (\x08), vertical tabs (\x0b), form feeds (\x0c) stripped
        dirty = "Clean\x00Text\x07With\x08Bad\x0bChars\x0cDone"
        assert normalize_text(dirty) == "CleanTextWithBadCharsDone"
        # ASCII DEL (0x7F) stripped
        assert normalize_text("Text\x7fDone") == "TextDone"
        # But \n and \t MUST be preserved
        preserved = "Line 1\nLine 2\tTabbed"
        assert normalize_text(preserved) == "Line 1\nLine 2\tTabbed"

    def test_multilingual_unicode_preservation(self):
        spanish = "¡Hola, mundo! ¿Cómo estás hoy?"
        japanese = "こんにちは、世界！"
        german = "Grüße über den Wolken"
        emoji = "Speech synthesis 🚀🎙️"
        assert normalize_text(spanish) == spanish
        assert normalize_text(japanese) == japanese
        assert normalize_text(german) == german
        assert normalize_text(emoji) == emoji


class TestCharacterCounting:
    """Tests deterministic character counting semantics (Prompt 10 §8, §9, §39)."""

    def test_empty_and_single_character(self):
        assert count_characters("") == 0
        assert count_characters("A") == 1
        assert count_characters(" ") == 1

    def test_spaces_tabs_newlines_counted(self):
        # Spaces count
        assert count_characters("Hello World") == 11
        # Newline counts
        assert count_characters("Hello\nWorld") == 11
        # Tab counts
        assert count_characters("Hello\tWorld") == 11

    def test_punctuation_and_numbers(self):
        assert count_characters("TTS: 100% ready!") == 16

    def test_multilingual_unicode_characters(self):
        # Accents and CJK
        assert count_characters("Café") == 4
        assert count_characters("日本語") == 3


class TestWordCounting:
    """Tests deterministic whitespace-aware word counting (Prompt 10 §10, §11, §40)."""

    def test_empty_and_whitespace_only(self):
        assert count_words("") == 0
        assert count_words(" ") == 0
        assert count_words("     ") == 0
        assert count_words("\n\t\r  ") == 0

    def test_single_and_multiple_words(self):
        assert count_words("Hello") == 1
        assert count_words("Hello World") == 2

    def test_multiple_spaces_no_phantom_words(self):
        assert count_words("Hello   World") == 2
        assert count_words("  Hello   World  ") == 2
        assert count_words("   One   Two   Three   ") == 3

    def test_newlines_and_tabs(self):
        assert count_words("Hello\nWorld") == 2
        assert count_words("Hello\tWorld") == 2
        assert count_words("Line 1\n\nLine 2\t\tLine 3") == 6

    def test_punctuation_containing_words(self):
        assert count_words("Hello, World!") == 2
        assert count_words("State-of-the-art TTS engine.") == 3


class TestTextProcessorClass:
    """Tests object-oriented TextProcessor service methods."""

    def test_processor_instance_methods(self):
        processor = TextProcessor(default_speaking_rate_wpm=150.0)
        raw = "  \r\nHello Bloop   Platform!  \r\n"
        normalized = processor.normalize(raw)
        assert normalized == "Hello Bloop   Platform!"
        assert processor.count_chars(normalized) == len("Hello Bloop   Platform!")
        assert processor.count_words(normalized) == 3

        metrics = processor.analyze(raw)
        assert metrics.character_count == len("Hello Bloop   Platform!")
        assert metrics.word_count == 3
        assert metrics.normalized_text == "Hello Bloop   Platform!"
        assert metrics.estimated_duration_seconds > 0.0
