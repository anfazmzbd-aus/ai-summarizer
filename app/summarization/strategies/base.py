"""
Base abstractions for summarization strategies.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol

from app.summarization.chunking.models import Chunk

from .models import MapReduceResult


MapFunction = Callable[[Chunk], str]
ReduceFunction = Callable[[Sequence[str]], str]


class SummarizationStrategy(Protocol):
    """
    Protocol implemented by summarization strategies.
    """

    def summarize(
        self,
        chunks: Sequence[Chunk],
    ) -> MapReduceResult:
        """
        Summarize an ordered collection of chunks.
        """
        ...


__all__ = [
    "MapFunction",
    "ReduceFunction",
    "SummarizationStrategy",
]
