"""
Tests for V9.2 token-aware document chunking.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking import (
    Chunk,
    ChunkingConfig,
    DeterministicTokenCounter,
    TextChunker,
)


def test_empty_input_returns_no_chunks():
    chunker = TextChunker()

    assert chunker.chunk("") == []


def test_whitespace_only_input_returns_no_chunks():
    chunker = TextChunker()

    assert chunker.chunk("   \n\n\t  ") == []


def test_token_counter_is_deterministic():
    counter = DeterministicTokenCounter()

    text = "Hello, world! This is deterministic."

    assert counter.count(text) == counter.count(text)
    assert counter.count(text) == 8


def test_token_counter_ignores_whitespace():
    counter = DeterministicTokenCounter()

    assert counter.count("hello world") == 2
    assert counter.count("hello    world") == 2
    assert counter.count("hello\nworld") == 2


def test_token_counter_counts_punctuation():
    counter = DeterministicTokenCounter()

    assert counter.count("Hello, world!") == 4


def test_config_defaults():
    config = ChunkingConfig()

    assert config.max_tokens == 512
    assert config.overlap_tokens == 0
    assert config.preserve_boundaries is True


@pytest.mark.parametrize("max_tokens", [0, -1])
def test_invalid_max_tokens_are_rejected(max_tokens):
    with pytest.raises(
        ValueError,
        match="max_tokens must be greater than zero",
    ):
        ChunkingConfig(max_tokens=max_tokens)


def test_negative_overlap_is_rejected():
    with pytest.raises(ValueError, match="overlap_tokens"):
        ChunkingConfig(
            max_tokens=10,
            overlap_tokens=-1,
        )


def test_overlap_must_be_smaller_than_max_tokens():
    with pytest.raises(ValueError, match="overlap_tokens"):
        ChunkingConfig(
            max_tokens=10,
            overlap_tokens=10,
        )


def test_text_smaller_than_limit_produces_one_chunk():
    text = "This is a short document."

    chunker = TextChunker(ChunkingConfig(max_tokens=20))

    chunks = chunker.chunk(text)

    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].text == text
    assert chunks[0].token_count == 6
    assert chunks[0].character_count == len(text)
    assert chunks[0].start_offset == 0
    assert chunks[0].end_offset == len(text)


def test_document_is_split_when_max_tokens_is_exceeded():
    text = "one two three four five six seven eight nine ten"

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=4,
            preserve_boundaries=False,
        )
    )

    chunks = chunker.chunk(text)

    assert len(chunks) == 3
    assert [chunk.token_count for chunk in chunks] == [
        4,
        4,
        2,
    ]


def test_every_chunk_respects_maximum_token_limit():
    text = " ".join(f"word{i}" for i in range(50))

    config = ChunkingConfig(
        max_tokens=7,
        preserve_boundaries=False,
    )

    chunks = TextChunker(config).chunk(text)

    assert chunks

    for chunk in chunks:
        assert chunk.token_count <= config.max_tokens


def test_chunk_order_is_deterministic():
    text = (
        "First paragraph contains information. "
        "Second paragraph contains more information. "
        "Third paragraph finishes the document."
    )

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=6,
            preserve_boundaries=False,
        )
    )

    first = chunker.chunk(text)
    second = chunker.chunk(text)

    assert first == second
    assert [chunk.index for chunk in first] == list(range(len(first)))


def test_sentence_boundary_is_preferred():
    text = (
        "First sentence is here. " "Second sentence is here. " "Third sentence is here."
    )

    counter = DeterministicTokenCounter()

    assert counter.count("First sentence is here.") == 5
    assert counter.count("First sentence is here. Second sentence is here.") == 10

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=10,
            preserve_boundaries=True,
        )
    )

    chunks = chunker.chunk(text)

    assert len(chunks) == 2
    assert chunks[0].text == ("First sentence is here. Second sentence is here.")


def test_paragraph_boundary_is_preferred():
    text = (
        "First paragraph contains several words.\n\n"
        "Second paragraph contains several words."
    )

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=7,
            preserve_boundaries=True,
        )
    )

    chunks = chunker.chunk(text)

    assert len(chunks) == 2
    assert chunks[0].text == ("First paragraph contains several words.")
    assert chunks[1].text == ("Second paragraph contains several words.")


def test_oversized_sentence_is_split_deterministically():
    text = "one two three four five six seven eight nine ten " "eleven twelve"

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=5,
            preserve_boundaries=True,
        )
    )

    chunks = chunker.chunk(text)

    assert len(chunks) == 3
    assert [chunk.token_count for chunk in chunks] == [
        5,
        5,
        2,
    ]


def test_oversized_segment_never_exceeds_limit():
    text = " ".join(f"token{i}" for i in range(100))

    config = ChunkingConfig(
        max_tokens=10,
        preserve_boundaries=True,
    )

    chunks = TextChunker(config).chunk(text)

    assert chunks

    assert all(chunk.token_count <= config.max_tokens for chunk in chunks)


def test_overlap_reuses_trailing_tokens():
    text = "one two three four five six seven eight"

    config = ChunkingConfig(
        max_tokens=4,
        overlap_tokens=2,
        preserve_boundaries=False,
    )

    chunks = TextChunker(config).chunk(text)

    assert [chunk.text for chunk in chunks] == [
        "one two three four",
        "three four five six",
        "five six seven eight",
    ]


def test_overlap_is_token_aware():
    text = "one two three four five six seven eight"

    config = ChunkingConfig(
        max_tokens=4,
        overlap_tokens=1,
        preserve_boundaries=False,
    )

    chunks = TextChunker(config).chunk(text)

    assert chunks[0].text == "one two three four"
    assert chunks[1].text == "four five six seven"
    assert chunks[2].text == "seven eight"


def test_source_offsets_are_exact():
    text = "Alpha beta. Gamma delta."

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=3,
            preserve_boundaries=False,
        )
    )

    chunks = chunker.chunk(text)

    for chunk in chunks:
        assert text[chunk.start_offset : chunk.end_offset] == chunk.text


def test_character_count_matches_chunk_text():
    text = "One two three four five six."

    chunks = TextChunker(
        ChunkingConfig(
            max_tokens=3,
            preserve_boundaries=False,
        )
    ).chunk(text)

    for chunk in chunks:
        assert chunk.character_count == len(chunk.text)


def test_token_count_matches_token_counter():
    text = "One two three four five six."

    counter = DeterministicTokenCounter()

    chunks = TextChunker(
        ChunkingConfig(
            max_tokens=3,
            preserve_boundaries=False,
        ),
        token_counter=counter,
    ).chunk(text)

    for chunk in chunks:
        assert chunk.token_count == counter.count(chunk.text)


def test_chunk_metadata_is_consistent():
    text = "First sentence. " "Second sentence. " "Third sentence."

    chunks = TextChunker(ChunkingConfig(max_tokens=4)).chunk(text)

    for index, chunk in enumerate(chunks):
        assert isinstance(chunk, Chunk)
        assert chunk.index == index
        assert chunk.token_count > 0
        assert chunk.character_count > 0
        assert chunk.start_offset >= 0
        assert chunk.end_offset > chunk.start_offset


def test_chunk_offsets_are_monotonically_ordered():
    text = "one two three four five six seven eight nine ten"

    chunks = TextChunker(
        ChunkingConfig(
            max_tokens=3,
            preserve_boundaries=False,
        )
    ).chunk(text)

    for previous, current in zip(chunks, chunks[1:]):
        assert current.start_offset > previous.start_offset
        assert current.end_offset > previous.end_offset


def test_unicode_text_is_supported():
    text = "Café résumé 東京 language."

    chunker = TextChunker(ChunkingConfig(max_tokens=20))

    chunks = chunker.chunk(text)

    assert len(chunks) == 1
    assert chunks[0].text == text


def test_custom_token_counter_is_supported():
    class FixedCounter:
        def count(self, text: str) -> int:
            return len(text.split())

    text = "one two three four"

    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=2,
            preserve_boundaries=False,
        ),
        token_counter=FixedCounter(),
    )

    chunks = chunker.chunk(text)

    assert [chunk.token_count for chunk in chunks] == [2, 2]


def test_no_runtime_or_provider_imports_are_required():
    from app.summarization.chunking import (
        Chunk,
        ChunkingConfig,
        DeterministicTokenCounter,
        TextChunker,
    )

    assert Chunk is not None
    assert ChunkingConfig is not None
    assert DeterministicTokenCounter is not None
    assert TextChunker is not None
