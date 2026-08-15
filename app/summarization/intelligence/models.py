"""
V9.3-M2 immutable document intelligence models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DocumentStructureType(str, Enum):
    """Deterministic high-level structural classification."""

    EMPTY = "empty"
    PROSE = "prose"
    STRUCTURED = "structured"
    CODE = "code"
    MIXED = "mixed"


@dataclass(frozen=True)
class DocumentProfile:
    """
    Deterministic, provider-independent profile of a source document.

    The profile describes observable document characteristics only. It does
    not infer semantic meaning and does not invoke a provider or model.
    """

    character_count: int
    token_count: int
    word_count: int
    unique_word_count: int
    paragraph_count: int
    sentence_count: int
    heading_count: int
    list_item_count: int
    code_block_count: int
    quote_block_count: int
    table_row_count: int
    average_sentence_tokens: float
    lexical_diversity: float
    structure_type: DocumentStructureType
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "character_count",
            "token_count",
            "word_count",
            "unique_word_count",
            "paragraph_count",
            "sentence_count",
            "heading_count",
            "list_item_count",
            "code_block_count",
            "quote_block_count",
            "table_row_count",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")

        if self.unique_word_count > self.word_count:
            raise ValueError("unique_word_count must not exceed word_count")

        if self.average_sentence_tokens < 0:
            raise ValueError("average_sentence_tokens must be non-negative")

        if not 0 <= self.lexical_diversity <= 1:
            raise ValueError("lexical_diversity must be between zero and one")

        if not isinstance(self.structure_type, DocumentStructureType):
            raise TypeError("structure_type must be a DocumentStructureType")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")


__all__ = ["DocumentProfile", "DocumentStructureType"]
