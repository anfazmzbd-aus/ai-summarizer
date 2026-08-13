"""
AI Summarizer V9.2

Token-aware document text chunker.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .models import Chunk, ChunkingConfig
from .token_counter import DeterministicTokenCounter, TokenCounter


_TOKEN_PATTERN = re.compile(
    r"\w+|[^\w\s]",
    re.UNICODE,
)

_SENTENCE_END_PATTERN = re.compile(r'[.!?](?:["\')\]]+)?(?=\s|$)')


@dataclass(frozen=True)
class _TokenSpan:
    """
    Internal token representation with source offsets.
    """

    text: str
    start: int
    end: int


class TextChunker:
    """
    Deterministic token-aware document chunker.

    The chunker:

    - handles empty input
    - enforces a configurable maximum token count
    - supports configurable token overlap
    - prefers paragraph and sentence boundaries
    - splits oversized segments deterministically
    - preserves source offsets
    - produces deterministic chunk ordering
    """

    def __init__(
        self,
        config: ChunkingConfig | None = None,
        token_counter: TokenCounter | None = None,
    ) -> None:
        self._config = config or ChunkingConfig()
        self._token_counter = token_counter or DeterministicTokenCounter()

    @property
    def config(self) -> ChunkingConfig:
        """Return the configured chunking policy."""
        return self._config

    @property
    def token_counter(self) -> TokenCounter:
        """Return the configured token counter."""
        return self._token_counter

    def chunk(self, text: str) -> list[Chunk]:
        """
        Split text into deterministic token-aware chunks.

        Empty or whitespace-only input returns an empty list.
        """
        if not text or not text.strip():
            return []

        tokens = self._token_spans(text)

        if not tokens:
            return []

        boundaries = self._preferred_boundaries(
            text,
            tokens,
        )

        ranges = self._build_ranges(
            tokens=tokens,
            boundaries=boundaries,
        )

        return [
            self._build_chunk(
                index=index,
                text=text,
                tokens=tokens,
                start_token=start,
                end_token=end,
            )
            for index, (start, end) in enumerate(ranges)
        ]

    def _token_spans(self, text: str) -> list[_TokenSpan]:
        return [
            _TokenSpan(
                text=match.group(0),
                start=match.start(),
                end=match.end(),
            )
            for match in _TOKEN_PATTERN.finditer(text)
        ]

    def _preferred_boundaries(
        self,
        text: str,
        tokens: list[_TokenSpan],
    ) -> set[int]:
        """
        Return token indexes immediately after preferred boundaries.

        Boundary indexes represent exclusive token positions.
        """
        if not self._config.preserve_boundaries:
            return set()

        boundaries: set[int] = set()

        for index, token in enumerate(tokens):
            token_end = token.end

            if _SENTENCE_END_PATTERN.search(text[token.start : token_end]):
                boundaries.add(index + 1)
                continue

            if index + 1 < len(tokens):
                gap = text[token.end : tokens[index + 1].start]

                if "\n\n" in gap or "\r\n\r\n" in gap:
                    boundaries.add(index + 1)

        boundaries.add(len(tokens))

        return boundaries

    def _build_ranges(
        self,
        tokens: list[_TokenSpan],
        boundaries: set[int],
    ) -> list[tuple[int, int]]:
        """
        Build deterministic token ranges.

        Chunk endpoints prefer sentence/paragraph boundaries. When no
        preferred boundary fits within the configured limit, the range
        ends exactly at max_tokens.

        Overlap is applied from the preceding chunk's trailing tokens.
        """
        max_tokens = self._config.max_tokens
        overlap_tokens = self._config.overlap_tokens

        ranges: list[tuple[int, int]] = []
        start = 0

        while start < len(tokens):
            remaining = len(tokens) - start

            if remaining <= max_tokens:
                ranges.append((start, len(tokens)))
                break

            hard_end = start + max_tokens

            preferred_end = self._latest_boundary(
                boundaries,
                start + 1,
                hard_end,
            )

            end = preferred_end or hard_end

            if end <= start:
                end = hard_end

            ranges.append((start, end))

            next_start = max(
                end - overlap_tokens,
                start + 1,
            )

            start = next_start

        return self._deduplicate_ranges(ranges)

    @staticmethod
    def _latest_boundary(
        boundaries: set[int],
        minimum: int,
        maximum: int,
    ) -> int | None:
        candidates = [
            boundary for boundary in boundaries if minimum <= boundary <= maximum
        ]

        if not candidates:
            return None

        return max(candidates)

    @staticmethod
    def _deduplicate_ranges(
        ranges: list[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        previous: tuple[int, int] | None = None

        for current in ranges:
            if current == previous:
                continue

            result.append(current)
            previous = current

        return result

    def _build_chunk(
        self,
        index: int,
        text: str,
        tokens: list[_TokenSpan],
        start_token: int,
        end_token: int,
    ) -> Chunk:
        start_offset = tokens[start_token].start
        end_offset = tokens[end_token - 1].end

        chunk_text = text[start_offset:end_offset]

        token_count = self._token_counter.count(chunk_text)

        return Chunk(
            index=index,
            text=chunk_text,
            token_count=token_count,
            character_count=len(chunk_text),
            start_offset=start_offset,
            end_offset=end_offset,
        )
