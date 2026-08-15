"""Tests for V9.3-M2 deterministic document intelligence."""

from __future__ import annotations

import pytest

from app.summarization.intelligence import (
    DocumentProfile,
    DocumentProfiler,
    DocumentStructureType,
)


def test_empty_document_profile_is_deterministic():
    profile = DocumentProfiler().profile("")

    assert isinstance(profile, DocumentProfile)
    assert profile.character_count == 0
    assert profile.token_count == 0
    assert profile.word_count == 0
    assert profile.unique_word_count == 0
    assert profile.paragraph_count == 0
    assert profile.sentence_count == 0
    assert profile.structure_type is DocumentStructureType.EMPTY
    assert profile.lexical_diversity == 0.0
    assert profile.average_sentence_tokens == 0.0


def test_prose_profile_counts_core_metrics():
    text = "Alpha beta. Gamma delta."

    profile = DocumentProfiler().profile(text)

    assert profile.character_count == len(text)
    assert profile.word_count == 4
    assert profile.unique_word_count == 4
    assert profile.sentence_count == 2
    assert profile.paragraph_count == 1
    assert profile.structure_type is DocumentStructureType.PROSE
    assert profile.lexical_diversity == 1.0
    assert profile.average_sentence_tokens > 0


def test_repeated_words_reduce_lexical_diversity():
    profile = DocumentProfiler().profile("word word word")

    assert profile.word_count == 3
    assert profile.unique_word_count == 1
    assert profile.lexical_diversity == pytest.approx(1 / 3)


def test_markdown_headings_and_lists_are_structured():
    text = "# Heading\n\n- First item\n- Second item"

    profile = DocumentProfiler().profile(text)

    assert profile.heading_count == 1
    assert profile.list_item_count == 2
    assert profile.structure_type is DocumentStructureType.STRUCTURED
    assert profile.metadata["has_markdown_headings"] is True
    assert profile.metadata["has_lists"] is True


def test_code_document_is_classified_as_code():
    text = "```python\ndef add(a, b):\n    return a + b\n```"

    profile = DocumentProfiler().profile(text)

    assert profile.code_block_count == 1
    assert profile.structure_type is DocumentStructureType.CODE
    assert profile.metadata["has_code"] is True


def test_code_signal_is_detected_without_fence():
    profile = DocumentProfiler().profile("def add(a, b):\n    return a + b")

    assert profile.structure_type is DocumentStructureType.CODE
    assert profile.metadata["has_code"] is True


def test_quote_and_table_signals_are_profiled():
    text = "> quoted\n\n| A | B |\n|---|---|\n| 1 | 2 |"

    profile = DocumentProfiler().profile(text)

    assert profile.quote_block_count == 1
    assert profile.table_row_count == 3
    assert profile.structure_type is DocumentStructureType.STRUCTURED
    assert profile.metadata["has_quotes"] is True
    assert profile.metadata["has_table"] is True


def test_multiple_paragraphs_are_counted():
    profile = DocumentProfiler().profile("First paragraph.\n\nSecond paragraph.")

    assert profile.paragraph_count == 2
    assert profile.sentence_count == 2


def test_profile_is_deterministic():
    profiler = DocumentProfiler()
    text = "# Heading\n\nAlpha beta. Gamma beta."

    assert profiler.profile(text) == profiler.profile(text)


def test_profile_is_immutable():
    profile = DocumentProfiler().profile("immutable")

    with pytest.raises(AttributeError):
        profile.word_count = 99  # type: ignore[misc]


def test_profiler_rejects_non_string_input():
    with pytest.raises(TypeError, match="text must be a string"):
        DocumentProfiler().profile(123)  # type: ignore[arg-type]


def test_custom_token_counter_is_supported():
    class FixedCounter:
        def count(self, text: str) -> int:
            return len(text.split())

    profile = DocumentProfiler(FixedCounter()).profile("one two three")

    assert profile.token_count == 3


def test_profiler_exposes_version_metadata():
    profile = DocumentProfiler().profile("versioned")

    assert profile.metadata["profiler_version"] == "v9.3-m2"


def test_profile_rejects_invalid_diversity():
    with pytest.raises(ValueError, match="lexical_diversity"):
        DocumentProfile(
            character_count=1,
            token_count=1,
            word_count=1,
            unique_word_count=1,
            paragraph_count=1,
            sentence_count=1,
            heading_count=0,
            list_item_count=0,
            code_block_count=0,
            quote_block_count=0,
            table_row_count=0,
            average_sentence_tokens=1.0,
            lexical_diversity=2.0,
            structure_type=DocumentStructureType.PROSE,
        )
