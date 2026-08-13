"""
AI Summarizer V9.2

Models for hierarchical summarization.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChunkGroup:
    """
    Ordered group of source chunks.

    A ChunkGroup represents the structural unit that will eventually
    become one summarization input at a hierarchy level.
    """

    group_index: int
    chunk_indexes: tuple[int, ...]
    token_count: int
    character_count: int

    def __post_init__(self) -> None:
        if self.group_index < 0:
            raise ValueError("group_index must be non-negative")

        if not self.chunk_indexes:
            raise ValueError("chunk_indexes must not be empty")

        if any(index < 0 for index in self.chunk_indexes):
            raise ValueError("chunk_indexes must contain non-negative indexes")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.character_count < 0:
            raise ValueError("character_count must be non-negative")


@dataclass(frozen=True)
class SummaryNode:
    """
    Immutable node in the hierarchical summarization tree.

    A leaf node corresponds to one source chunk.

    A non-leaf node represents an aggregation of child nodes.
    """

    node_id: str
    level: int
    source_chunk_indexes: tuple[int, ...]
    source_text: str = ""
    summary: str | None = None
    children: tuple["SummaryNode", ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must not be empty")

        if self.level < 0:
            raise ValueError("level must be non-negative")

        if any(index < 0 for index in self.source_chunk_indexes):
            raise ValueError(
                "source_chunk_indexes must contain " "non-negative indexes"
            )

        if len(set(self.source_chunk_indexes)) != len(self.source_chunk_indexes):
            raise ValueError("source_chunk_indexes must not contain duplicates")

        if self.children:
            child_indexes: list[int] = []

            for child in self.children:
                child_indexes.extend(child.source_chunk_indexes)

            if tuple(child_indexes) != self.source_chunk_indexes:
                raise ValueError(
                    "source_chunk_indexes must preserve "
                    "child provenance and ordering"
                )

    @property
    def is_leaf(self) -> bool:
        """Return whether this node represents a source chunk."""
        return not self.children

    @property
    def child_count(self) -> int:
        """Return the number of direct child nodes."""
        return len(self.children)


@dataclass(frozen=True)
class HierarchyConfig:
    """
    Configuration for hierarchical grouping.

    max_children_per_node:
        Maximum number of children represented by a parent node.

    maximum_levels:
        Maximum number of hierarchy levels including level zero.

    preserve_order:
        Preserve source chunk ordering throughout the hierarchy.
    """

    max_children_per_node: int = 4
    maximum_levels: int = 16
    preserve_order: bool = True

    def __post_init__(self) -> None:
        if self.max_children_per_node <= 0:
            raise ValueError("max_children_per_node must be greater than zero")

        if self.maximum_levels <= 0:
            raise ValueError("maximum_levels must be greater than zero")
