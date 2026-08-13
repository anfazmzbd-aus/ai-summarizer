"""
AI Summarizer V9.2

Deterministic hierarchical summarization structure builder.
"""

from __future__ import annotations

from app.summarization.chunking.models import Chunk

from .grouping import ChunkGrouper
from .models import HierarchyConfig, SummaryNode


class HierarchyBuilder:
    """
    Build a deterministic hierarchy from document chunks.

    This class does not perform summarization.

    It establishes:

    - hierarchy levels
    - grouping
    - provenance
    - deterministic node identifiers
    - source ordering

    Actual LLM summarization belongs to a later strategy layer.
    """

    def __init__(
        self,
        config: HierarchyConfig | None = None,
    ) -> None:
        self._config = config or HierarchyConfig()
        self._grouper = ChunkGrouper(self._config)

    @property
    def config(self) -> HierarchyConfig:
        """Return the hierarchy configuration."""
        return self._config

    def build(
        self,
        chunks: list[Chunk] | tuple[Chunk, ...],
    ) -> SummaryNode | None:
        """
        Build a hierarchy from source chunks.

        Empty input returns None.

        A single chunk produces a level-zero leaf.

        Multiple chunks produce one or more aggregation levels.
        """
        if not chunks:
            return None

        ordered_chunks = self._ordered_chunks(chunks)

        leaves = tuple(self._build_leaf(chunk) for chunk in ordered_chunks)

        if len(leaves) == 1:
            return leaves[0]

        return self._build_levels(leaves)

    def leaves(
        self,
        root: SummaryNode | None,
    ) -> tuple[SummaryNode, ...]:
        """
        Return all leaf nodes in source order.
        """
        if root is None:
            return ()

        result: list[SummaryNode] = []

        def visit(node: SummaryNode) -> None:
            if node.is_leaf:
                result.append(node)
                return

            for child in node.children:
                visit(child)

        visit(root)

        return tuple(result)

    def _build_leaf(self, chunk: Chunk) -> SummaryNode:
        return SummaryNode(
            node_id=f"chunk-{chunk.index}",
            level=0,
            source_chunk_indexes=(chunk.index,),
            source_text=chunk.text,
        )

    def _build_levels(
        self,
        nodes: tuple[SummaryNode, ...],
    ) -> SummaryNode:
        current = nodes
        level = 0

        while len(current) > 1:
            next_level = level + 1

            if next_level >= self._config.maximum_levels:
                raise ValueError(
                    "maximum_levels is insufficient to " "represent the hierarchy"
                )

            groups = self._group_nodes(current)

            current = tuple(
                self._build_parent(
                    level=next_level,
                    group_index=index,
                    children=group,
                )
                for index, group in enumerate(groups)
            )

            level = next_level

        return current[0]

    def _group_nodes(
        self,
        nodes: tuple[SummaryNode, ...],
    ) -> list[tuple[SummaryNode, ...]]:
        size = self._config.max_children_per_node

        return [nodes[start : start + size] for start in range(0, len(nodes), size)]

    @staticmethod
    def _build_parent(
        level: int,
        group_index: int,
        children: tuple[SummaryNode, ...],
    ) -> SummaryNode:
        source_indexes: list[int] = []

        for child in children:
            source_indexes.extend(child.source_chunk_indexes)

        return SummaryNode(
            node_id=f"level-{level}-group-{group_index}",
            level=level,
            source_chunk_indexes=tuple(source_indexes),
            children=children,
        )

    def _ordered_chunks(
        self,
        chunks: list[Chunk] | tuple[Chunk, ...],
    ) -> list[Chunk]:
        if self._config.preserve_order:
            return sorted(
                chunks,
                key=lambda chunk: chunk.index,
            )

        return list(chunks)
