"""
V9.3-M1 deterministic intelligent summarization planner.
"""

from __future__ import annotations

import hashlib

from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.intelligence import (
    DocumentProfiler,
    # IntentClassification,
    IntentClassifier,
    SummarizationIntent,
)
from app.summarization.strategies.models import StrategySelectionInput
from app.summarization.strategies.selector import SummarizationStrategySelector

from .models import SummarizationPlan


class SummarizationPlanner:
    """
    Build a deterministic plan over the existing V9.2 components.

    The planner owns orchestration only. It delegates document chunking to
    TextChunker and strategy selection to SummarizationStrategySelector.
    No provider, LLM, network, or execution dependency is introduced.
    """

    planner_version = "v9.3-m1"

    def __init__(
        self,
        chunker: TextChunker,
        selector: SummarizationStrategySelector | None = None,
        profiler: DocumentProfiler | None = None,
        intent_classifier: IntentClassifier | None = None,
    ) -> None:
        if not isinstance(chunker, TextChunker):
            raise TypeError("chunker must be a TextChunker")

        self._chunker = chunker
        self._selector = selector or SummarizationStrategySelector()
        self._profiler = profiler or DocumentProfiler(
            token_counter=self._chunker.token_counter
        )
        self._intent_classifier = intent_classifier or IntentClassifier()

    @property
    def chunker(self) -> TextChunker:
        """Return the configured V9.2 chunker."""
        return self._chunker

    @property
    def selector(self) -> SummarizationStrategySelector:
        """Return the configured V9.2 strategy selector."""
        return self._selector

    @property
    def profiler(self) -> DocumentProfiler:
        """Return the configured V9.3-M2 document profiler."""
        return self._profiler

    def plan(
        self,
        text: str,
        *,
        intent: SummarizationIntent | str | None = None,
    ) -> SummarizationPlan:
        """
        Build an immutable, deterministic plan for a source document.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        profile = self._profiler.profile(text)
        intent_classification = self._intent_classifier.classify(text, intent=intent)
        chunks = tuple(self._chunker.chunk(text))
        token_count = sum(chunk.token_count for chunk in chunks)
        chunk_count = len(chunks)

        selection = self._selector.select(
            StrategySelectionInput(
                token_count=token_count,
                chunk_count=chunk_count,
            )
        )

        return SummarizationPlan(
            strategy=selection.strategy,
            selection=selection,
            chunks=chunks,
            token_count=token_count,
            chunk_count=chunk_count,
            source_character_count=len(text),
            source_digest=self._digest(text),
            document_profile=profile,
            intent=intent_classification.intent,
            intent_classification=intent_classification,
            metadata={
                "planner_version": self.planner_version,
                "chunk_indexes": tuple(chunk.index for chunk in chunks),
                "strategy_reason": selection.reason,
                "structure_type": profile.structure_type.value,
                "paragraph_count": profile.paragraph_count,
                "sentence_count": profile.sentence_count,
                "intent": intent_classification.intent.value,
                "intent_confidence": intent_classification.confidence,
                "intent_explicit": intent_classification.explicit,
                "intent_matches": intent_classification.matched_terms,
            },
        )

    @staticmethod
    def _digest(text: str) -> str:
        """
        Return a deterministic SHA-256 digest of the source text.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
