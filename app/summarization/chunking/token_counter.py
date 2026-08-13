"""
AI Summarizer V9.2

Deterministic token counting.

This module intentionally does not depend on an LLM provider or a
provider-specific tokenizer. It provides a stable lexical token model
for deterministic chunking and testing.
"""

from __future__ import annotations

import re
from typing import Protocol


_TOKEN_PATTERN = re.compile(
    r"\w+|[^\w\s]",
    re.UNICODE,
)


class TokenCounter(Protocol):
    """
    Protocol for deterministic token counting.
    """

    def count(self, text: str) -> int:
        """
        Return the number of tokens in text.
        """
        ...


class DeterministicTokenCounter:
    """
    Deterministic lexical token counter.

    Tokenization rules:

    - word-like sequences are one token
    - punctuation and symbols are individual tokens
    - whitespace is not a token
    - Unicode word characters are supported
    - the same input always produces the same count

    This is intentionally model-independent. A provider/model-specific
    tokenizer can be introduced later without changing the Chunk model
    or TextChunker contract.
    """

    def count(self, text: str) -> int:
        """
        Count deterministic lexical tokens.
        """
        if not text:
            return 0

        return sum(1 for _ in _TOKEN_PATTERN.finditer(text))

    def tokenize(self, text: str) -> tuple[str, ...]:
        """
        Return deterministic lexical tokens.
        """
        if not text:
            return ()

        return tuple(match.group(0) for match in _TOKEN_PATTERN.finditer(text))
