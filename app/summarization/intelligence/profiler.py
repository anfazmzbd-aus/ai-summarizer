"""
V9.3-M2 deterministic document profiler.
"""

from __future__ import annotations

import re

from app.summarization.chunking.token_counter import (
    DeterministicTokenCounter,
    TokenCounter,
)

from .models import DocumentProfile, DocumentStructureType

_WORD_PATTERN = re.compile(r"\b[\w']+\b", re.UNICODE)
_SENTENCE_PATTERN = re.compile(r"[^.!?\n]+[.!?]+(?=\s|$)|[^.!?\n]+$", re.MULTILINE)
_HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s+\S+", re.MULTILINE)
_LIST_PATTERN = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)\S+", re.MULTILINE)
_QUOTE_PATTERN = re.compile(r"^\s*>\s+\S+", re.MULTILINE)
_TABLE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_CODE_FENCE_PATTERN = re.compile(r"^\s*```.*$", re.MULTILINE)
_CODE_SIGNAL_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:def |class |import |from |function |const |let |var |#include )"
)


class DocumentProfiler:
    """
    Build a deterministic structural profile from source text.

    The profiler is intentionally limited to observable textual signals. It
    does not classify topics, intent, sentiment, or meaning.
    """

    profiler_version = "v9.3-m2"

    def __init__(self, token_counter: TokenCounter | None = None) -> None:
        self._token_counter = token_counter or DeterministicTokenCounter()

    @property
    def token_counter(self) -> TokenCounter:
        """Return the configured deterministic token counter."""
        return self._token_counter

    def profile(self, text: str) -> DocumentProfile:
        """Return a deterministic profile for ``text``."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        character_count = len(text)
        words = [match.group(0).casefold() for match in _WORD_PATTERN.finditer(text)]
        word_count = len(words)
        unique_word_count = len(set(words))
        token_count = self._token_counter.count(text)
        paragraphs = self._paragraphs(text)
        sentences = self._sentences(text)
        sentence_token_counts = [
            self._token_counter.count(sentence) for sentence in sentences
        ]

        heading_count = len(_HEADING_PATTERN.findall(text))
        list_item_count = len(_LIST_PATTERN.findall(text))
        code_block_count = len(_CODE_FENCE_PATTERN.findall(text)) // 2
        quote_block_count = len(_QUOTE_PATTERN.findall(text))
        table_row_count = len(_TABLE_PATTERN.findall(text))

        structure_type = self._classify(
            text=text,
            word_count=word_count,
            heading_count=heading_count,
            list_item_count=list_item_count,
            code_block_count=code_block_count,
            quote_block_count=quote_block_count,
            table_row_count=table_row_count,
        )

        return DocumentProfile(
            character_count=character_count,
            token_count=token_count,
            word_count=word_count,
            unique_word_count=unique_word_count,
            paragraph_count=len(paragraphs),
            sentence_count=len(sentences),
            heading_count=heading_count,
            list_item_count=list_item_count,
            code_block_count=code_block_count,
            quote_block_count=quote_block_count,
            table_row_count=table_row_count,
            average_sentence_tokens=(
                sum(sentence_token_counts) / len(sentence_token_counts)
                if sentence_token_counts
                else 0.0
            ),
            lexical_diversity=(unique_word_count / word_count if word_count else 0.0),
            structure_type=structure_type,
            metadata={
                "profiler_version": self.profiler_version,
                "has_markdown_headings": heading_count > 0,
                "has_lists": list_item_count > 0,
                "has_code": code_block_count > 0
                or bool(_CODE_SIGNAL_PATTERN.search(text)),
                "has_quotes": quote_block_count > 0,
                "has_table": table_row_count > 0,
            },
        )

    @staticmethod
    def _paragraphs(text: str) -> list[str]:
        return [part for part in re.split(r"(?:\r?\n){2,}", text) if part.strip()]

    @staticmethod
    def _sentences(text: str) -> list[str]:
        return [
            match.group(0).strip()
            for match in _SENTENCE_PATTERN.finditer(text)
            if match.group(0).strip()
        ]

    @staticmethod
    def _classify(
        *,
        text: str,
        word_count: int,
        heading_count: int,
        list_item_count: int,
        code_block_count: int,
        quote_block_count: int,
        table_row_count: int,
    ) -> DocumentStructureType:
        if not text.strip():
            return DocumentStructureType.EMPTY

        code_signal = code_block_count > 0 or bool(_CODE_SIGNAL_PATTERN.search(text))
        structured_signals = (
            heading_count + list_item_count + quote_block_count + table_row_count
        )

        if code_signal and structured_signals > 0:
            return DocumentStructureType.MIXED

        if code_signal:
            return DocumentStructureType.CODE

        if structured_signals > 0:
            return DocumentStructureType.STRUCTURED

        return DocumentStructureType.PROSE


__all__ = ["DocumentProfiler"]
