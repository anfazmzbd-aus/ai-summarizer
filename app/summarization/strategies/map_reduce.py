"""
Deterministic Map-Reduce summarization strategy.

The strategy deliberately has no dependency on a concrete LLM provider.
MAP and REDUCE behavior are injected through callables.
"""

from __future__ import annotations

from collections.abc import Sequence

# from typing import Any

from app.summarization.chunking.models import Chunk

from .base import MapFunction, ReduceFunction
from .models import MapReduceResult, MapResult, ReduceInput


class MapReduceStrategy:
    """
    Deterministic Map-Reduce summarization strategy.

    MAP executes sequentially in source order.

    REDUCE receives summaries in exactly the same order as the source
    chunks.

    No concurrency or provider-specific behavior is introduced here.
    """

    def __init__(
        self,
        map_fn: MapFunction,
        reduce_fn: ReduceFunction,
    ) -> None:
        if not callable(map_fn):
            raise TypeError("map_fn must be callable")

        if not callable(reduce_fn):
            raise TypeError("reduce_fn must be callable")

        self._map_fn = map_fn
        self._reduce_fn = reduce_fn

    def summarize(
        self,
        chunks: Sequence[Chunk],
    ) -> MapReduceResult:
        """
        Execute MAP followed by REDUCE.

        Empty input produces an empty result without invoking either
        callable.
        """
        normalized_chunks = tuple(chunks)

        if not normalized_chunks:
            return MapReduceResult(
                summary="",
                map_results=(),
                source_chunk_indexes=(),
                metadata={
                    "map_count": 0,
                    "reduced": False,
                },
            )

        map_results: list[MapResult] = []

        for chunk in normalized_chunks:
            self._validate_chunk(chunk)

            summary = self._map_fn(chunk)

            if not isinstance(summary, str):
                raise TypeError("map_fn must return a string")

            map_results.append(
                MapResult(
                    chunk_index=chunk.index,
                    summary=summary,
                    token_count=chunk.token_count,  # source chunk token count processed by MAP.
                )
            )

        ordered_results = tuple(map_results)

        reduce_input = ReduceInput(
            results=ordered_results,
            source_chunk_indexes=tuple(
                result.chunk_index for result in ordered_results
            ),
            metadata={
                "map_count": len(ordered_results),
            },
        )

        summary = self._reduce(
            reduce_input,
        )

        return MapReduceResult(
            summary=summary,
            map_results=ordered_results,
            source_chunk_indexes=reduce_input.source_chunk_indexes,
            metadata={
                "map_count": len(ordered_results),
                "reduced": True,
            },
        )

    def _reduce(
        self,
        reduce_input: ReduceInput,
    ) -> str:
        """
        Execute REDUCE using ordered MAP summaries.

        A single chunk still passes through REDUCE so the strategy has
        one consistent semantic contract.
        """
        summaries = tuple(result.summary for result in reduce_input.results)

        summary = self._reduce_fn(summaries)

        if not isinstance(summary, str):
            raise TypeError("reduce_fn must return a string")

        return summary

    @staticmethod
    def _validate_chunk(chunk: Chunk) -> None:
        """Validate the minimum chunk contract required by M4."""
        if not isinstance(chunk, Chunk):
            raise TypeError("chunks must contain Chunk instances")

        if chunk.index < 0:
            raise ValueError("chunk.index must be non-negative")


__all__ = ["MapReduceStrategy"]
