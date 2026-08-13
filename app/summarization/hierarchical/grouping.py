"""
AI Summarizer V9.2

Deterministic grouping of document chunks.
"""

from __future__ import annotations

from app.summarization.chunking.models import Chunk

from .models import ChunkGroup, HierarchyConfig


class ChunkGrouper:
    """
    Deterministically group source chunks.

    The grouper is intentionally independent of any summarization
    provider. It only establishes structural grouping and metadata.
    """

    def __init__(
        self,
        config: HierarchyConfig | None = None,
    ) -> None:
        self._config = config or HierarchyConfig()

    @property
    def config(self) -> HierarchyConfig:
        """Return the grouping configuration."""
        return self._config

    def group(
        self,
        chunks: list[Chunk] | tuple[Chunk, ...],
    ) -> list[ChunkGroup]:
        """
        Group chunks according to max_children_per_node.

        Empty input produces an empty list.
        """
        if not chunks:
            return []

        ordered_chunks = self._ordered_chunks(chunks)

        groups: list[ChunkGroup] = []
        size = self._config.max_children_per_node

        for group_index, start in enumerate(range(0, len(ordered_chunks), size)):
            group_chunks = ordered_chunks[start : start + size]

            groups.append(
                ChunkGroup(
                    group_index=group_index,
                    chunk_indexes=tuple(chunk.index for chunk in group_chunks),
                    token_count=sum(chunk.token_count for chunk in group_chunks),
                    character_count=sum(
                        chunk.character_count for chunk in group_chunks
                    ),
                )
            )

        return groups

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
