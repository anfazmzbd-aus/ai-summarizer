"""
Deterministic context-preserving aggregation.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.summarization.chunking.models import Chunk
from app.summarization.strategies.models import MapResult

from .models import AggregatedContext, ContextEnvelope


class ContextAggregator:
    """
    Build contextual envelopes from source chunks and MAP results.

    The aggregator does not call an LLM and does not modify either the
    source chunks or MapResult instances.
    """

    def aggregate(
        self,
        chunks: Sequence[Chunk],
        map_results: Sequence[MapResult],
    ) -> AggregatedContext:
        """
        Aggregate chunks and their MAP results while preserving order
        and provenance.
        """
        normalized_chunks = tuple(chunks)
        normalized_results = tuple(map_results)

        if not normalized_chunks:
            if normalized_results:
                raise ValueError("map_results cannot be provided without chunks")

            return AggregatedContext.empty()

        if len(normalized_chunks) != len(normalized_results):
            raise ValueError("chunks and map_results must have equal lengths")

        self._validate_chunks(normalized_chunks)
        self._validate_results(normalized_results)

        envelopes: list[ContextEnvelope] = []

        for position, (chunk, result) in enumerate(
            zip(normalized_chunks, normalized_results)
        ):
            if chunk.index != result.chunk_index:
                raise ValueError("MapResult provenance does not match source chunk")

            preceding_index = (
                normalized_chunks[position - 1].index if position > 0 else None
            )

            following_index = (
                normalized_chunks[position + 1].index
                if position < len(normalized_chunks) - 1
                else None
            )

            envelopes.append(
                ContextEnvelope(
                    chunk_index=chunk.index,
                    summary=result.summary,
                    source_text=chunk.text,
                    start_offset=chunk.start_offset,
                    end_offset=chunk.end_offset,
                    token_count=chunk.token_count,
                    character_count=chunk.character_count,
                    preceding_chunk_index=preceding_index,
                    following_chunk_index=following_index,
                    metadata=dict(result.metadata),
                )
            )

        ordered_envelopes = tuple(envelopes)

        return AggregatedContext(
            envelopes=ordered_envelopes,
            source_chunk_indexes=tuple(
                envelope.chunk_index for envelope in ordered_envelopes
            ),
            start_offset=ordered_envelopes[0].start_offset,
            end_offset=ordered_envelopes[-1].end_offset,
            total_tokens=sum(envelope.token_count for envelope in ordered_envelopes),
            total_characters=sum(
                envelope.character_count for envelope in ordered_envelopes
            ),
            metadata={
                "chunk_count": len(ordered_envelopes),
                "source_start_offset": ordered_envelopes[0].start_offset,
                "source_end_offset": ordered_envelopes[-1].end_offset,
            },
        )

    @staticmethod
    def _validate_chunks(
        chunks: Sequence[Chunk],
    ) -> None:
        indexes: list[int] = []

        for chunk in chunks:
            if not isinstance(chunk, Chunk):
                raise TypeError("chunks must contain Chunk instances")

            if chunk.index < 0:
                raise ValueError("chunk.index must be non-negative")

            indexes.append(chunk.index)

        if len(indexes) != len(set(indexes)):
            raise ValueError("chunks must not contain duplicate indexes")

        if indexes != sorted(indexes):
            raise ValueError("chunks must be provided in source order")

    @staticmethod
    def _validate_results(
        results: Sequence[MapResult],
    ) -> None:
        indexes: list[int] = []

        for result in results:
            if not isinstance(result, MapResult):
                raise TypeError("map_results must contain MapResult instances")

            indexes.append(result.chunk_index)

        if len(indexes) != len(set(indexes)):
            raise ValueError("map_results must not contain duplicate chunk indexes")

        if indexes != sorted(indexes):
            raise ValueError("map_results must be provided in source order")


__all__ = ["ContextAggregator"]
