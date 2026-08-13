"""
Tests for V9.2 hierarchical summarization structure.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking import (
    Chunk,
    ChunkingConfig,
    TextChunker,
)
from app.summarization.hierarchical import (
    HierarchyBuilder,
    HierarchyConfig,
    SummaryNode,
)


def make_chunks(count: int) -> list[Chunk]:
    text = " ".join(f"chunk{i}" for i in range(count))

    return TextChunker(
        ChunkingConfig(
            max_tokens=1,
            preserve_boundaries=False,
        )
    ).chunk(text)


def test_empty_input_returns_none():
    builder = HierarchyBuilder()

    assert builder.build([]) is None


def test_single_chunk_produces_leaf_root():
    chunks = make_chunks(1)

    root = HierarchyBuilder().build(chunks)

    assert root is not None
    assert root.is_leaf is True
    assert root.level == 0
    assert root.node_id == "chunk-0"
    assert root.source_chunk_indexes == (0,)
    assert root.source_text == chunks[0].text
    assert root.children == ()


def test_multiple_chunks_produce_hierarchy():
    chunks = make_chunks(4)

    root = HierarchyBuilder(HierarchyConfig(max_children_per_node=2)).build(chunks)

    assert root is not None
    assert root.level == 2
    assert root.child_count == 2
    assert root.source_chunk_indexes == (
        0,
        1,
        2,
        3,
    )

    assert root.children[0].level == 1
    assert root.children[1].level == 1

    assert root.children[0].source_chunk_indexes == (
        0,
        1,
    )

    assert root.children[1].source_chunk_indexes == (
        2,
        3,
    )


def test_leaf_nodes_are_level_zero():
    chunks = make_chunks(4)

    root = HierarchyBuilder(HierarchyConfig(max_children_per_node=2)).build(chunks)

    assert root is not None

    leaves = HierarchyBuilder().leaves(root)

    assert all(leaf.level == 0 for leaf in leaves)
    assert all(leaf.is_leaf for leaf in leaves)


def test_leaf_provenance_matches_source_chunks():
    chunks = make_chunks(5)

    builder = HierarchyBuilder(HierarchyConfig(max_children_per_node=2))

    root = builder.build(chunks)

    assert root is not None

    leaves = builder.leaves(root)

    assert [leaf.source_chunk_indexes[0] for leaf in leaves] == [0, 1, 2, 3, 4]


def test_every_source_chunk_occurs_once_in_leaves():
    chunks = make_chunks(10)

    builder = HierarchyBuilder(HierarchyConfig(max_children_per_node=3))

    root = builder.build(chunks)

    assert root is not None

    leaves = builder.leaves(root)

    indexes = [leaf.source_chunk_indexes[0] for leaf in leaves]

    assert len(indexes) == len(set(indexes))
    assert sorted(indexes) == list(range(10))


def test_provenance_is_preserved_at_root():
    chunks = make_chunks(10)

    root = HierarchyBuilder(HierarchyConfig(max_children_per_node=3)).build(chunks)

    assert root is not None

    assert root.source_chunk_indexes == tuple(range(10))


def test_source_order_is_preserved():
    chunks = make_chunks(8)

    builder = HierarchyBuilder(
        HierarchyConfig(
            max_children_per_node=2,
            preserve_order=True,
        )
    )

    root = builder.build(
        [
            chunks[7],
            chunks[2],
            chunks[0],
            chunks[5],
            chunks[1],
            chunks[6],
            chunks[3],
            chunks[4],
        ]
    )

    assert root is not None

    leaves = builder.leaves(root)

    assert [leaf.source_chunk_indexes[0] for leaf in leaves] == list(range(8))


def test_hierarchy_is_deterministic():
    chunks = make_chunks(12)

    builder = HierarchyBuilder(HierarchyConfig(max_children_per_node=3))

    first = builder.build(chunks)
    second = builder.build(chunks)

    assert first == second


def test_node_ids_are_deterministic():
    chunks = make_chunks(7)

    builder = HierarchyBuilder(HierarchyConfig(max_children_per_node=2))

    root = builder.build(chunks)

    assert root is not None

    leaves = builder.leaves(root)

    assert [leaf.node_id for leaf in leaves] == [
        "chunk-0",
        "chunk-1",
        "chunk-2",
        "chunk-3",
        "chunk-4",
        "chunk-5",
        "chunk-6",
    ]


def test_hierarchy_has_expected_levels():
    chunks = make_chunks(16)

    builder = HierarchyBuilder(HierarchyConfig(max_children_per_node=2))

    root = builder.build(chunks)

    assert root is not None
    assert root.level == 4


def test_uneven_hierarchy_preserves_all_chunks():
    chunks = make_chunks(7)

    builder = HierarchyBuilder(HierarchyConfig(max_children_per_node=3))

    root = builder.build(chunks)

    assert root is not None

    assert root.source_chunk_indexes == tuple(range(7))

    leaves = builder.leaves(root)

    assert len(leaves) == 7


def test_children_preserve_provenance_order():
    chunks = make_chunks(6)

    root = HierarchyBuilder(HierarchyConfig(max_children_per_node=2)).build(chunks)

    assert root is not None

    assert root.level == 3

    assert root.children[0].source_chunk_indexes == (
        0,
        1,
        2,
        3,
    )

    assert root.children[1].source_chunk_indexes == (
        4,
        5,
    )

    assert root.children[0].children[0].source_chunk_indexes == (
        0,
        1,
    )

    assert root.children[0].children[1].source_chunk_indexes == (
        2,
        3,
    )

    assert root.children[1].children[0].source_chunk_indexes == (
        4,
        5,
    )


def test_summary_node_rejects_empty_id():
    with pytest.raises(
        ValueError,
        match="node_id",
    ):
        SummaryNode(
            node_id="",
            level=0,
            source_chunk_indexes=(0,),
        )


def test_summary_node_rejects_duplicate_provenance():
    with pytest.raises(
        ValueError,
        match="duplicates",
    ):
        SummaryNode(
            node_id="test",
            level=0,
            source_chunk_indexes=(0, 0),
        )


def test_summary_node_rejects_negative_level():
    with pytest.raises(
        ValueError,
        match="level",
    ):
        SummaryNode(
            node_id="test",
            level=-1,
            source_chunk_indexes=(0,),
        )


def test_maximum_levels_is_enforced():
    chunks = make_chunks(8)

    builder = HierarchyBuilder(
        HierarchyConfig(
            max_children_per_node=2,
            maximum_levels=2,
        )
    )

    with pytest.raises(
        ValueError,
        match="maximum_levels",
    ):
        builder.build(chunks)
