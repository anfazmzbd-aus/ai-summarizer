"""
Tests for V9.2 hierarchical chunk grouping.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking import (
    Chunk,
    ChunkingConfig,
    TextChunker,
)
from app.summarization.hierarchical import (
    ChunkGrouper,
    HierarchyConfig,
)


def make_chunks(count: int) -> list[Chunk]:
    text = " ".join(f"chunk{i}" for i in range(count))

    return TextChunker(
        ChunkingConfig(
            max_tokens=1,
            preserve_boundaries=False,
        )
    ).chunk(text)


def test_empty_chunks_produce_no_groups():
    grouper = ChunkGrouper()

    assert grouper.group([]) == []


def test_single_chunk_produces_one_group():
    chunks = make_chunks(1)

    groups = ChunkGrouper(HierarchyConfig(max_children_per_node=4)).group(chunks)

    assert len(groups) == 1
    assert groups[0].chunk_indexes == (0,)


def test_chunks_are_grouped_by_configured_size():
    chunks = make_chunks(10)

    groups = ChunkGrouper(HierarchyConfig(max_children_per_node=3)).group(chunks)

    assert [group.chunk_indexes for group in groups] == [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (9,),
    ]


def test_final_group_may_be_smaller():
    chunks = make_chunks(5)

    groups = ChunkGrouper(HierarchyConfig(max_children_per_node=2)).group(chunks)

    assert groups[-1].chunk_indexes == (4,)


def test_group_indexes_are_deterministic():
    chunks = make_chunks(7)

    groups = ChunkGrouper(HierarchyConfig(max_children_per_node=3)).group(chunks)

    assert [group.group_index for group in groups] == [
        0,
        1,
        2,
    ]


def test_group_metadata_is_aggregated():
    chunks = make_chunks(3)

    groups = ChunkGrouper(HierarchyConfig(max_children_per_node=3)).group(chunks)

    group = groups[0]

    assert group.token_count == sum(chunk.token_count for chunk in chunks)
    assert group.character_count == sum(chunk.character_count for chunk in chunks)


def test_grouping_preserves_chunk_order():
    chunks = make_chunks(4)

    shuffled = [
        chunks[3],
        chunks[1],
        chunks[0],
        chunks[2],
    ]

    groups = ChunkGrouper(
        HierarchyConfig(
            max_children_per_node=2,
            preserve_order=True,
        )
    ).group(shuffled)

    assert [group.chunk_indexes for group in groups] == [
        (0, 1),
        (2, 3),
    ]


@pytest.mark.parametrize(
    "max_children",
    [0, -1],
)
def test_invalid_group_size_is_rejected(max_children):
    with pytest.raises(
        ValueError,
        match="max_children_per_node",
    ):
        HierarchyConfig(max_children_per_node=max_children)


@pytest.mark.parametrize(
    "maximum_levels",
    [0, -1],
)
def test_invalid_maximum_levels_is_rejected(maximum_levels):
    with pytest.raises(
        ValueError,
        match="maximum_levels",
    ):
        HierarchyConfig(maximum_levels=maximum_levels)
