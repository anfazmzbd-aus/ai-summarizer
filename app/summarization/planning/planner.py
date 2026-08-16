"""
V9.3 deterministic intelligent summarization planner.
"""

from __future__ import annotations

import hashlib

from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.intelligence import (
    DocumentProfiler,
    IntentClassifier,
    SummarizationIntent,
)
from app.summarization.strategies.models import (
    StrategySelection,
    StrategySelectionInput,
)
from app.summarization.strategies.selector import SummarizationStrategySelector

from .adaptive import AdaptiveStrategyPlanner
from .models import SummarizationPlan


class SummarizationPlanner:
    """Build a deterministic plan over the existing V9.2 components."""

    planner_version = "v9.3-m1"

    def __init__(
        self,
        chunker: TextChunker,
        selector: SummarizationStrategySelector | None = None,
        profiler: DocumentProfiler | None = None,
        intent_classifier: IntentClassifier | None = None,
        adaptive_planner: AdaptiveStrategyPlanner | None = None,
    ) -> None:
        if not isinstance(chunker, TextChunker):
            raise TypeError("chunker must be a TextChunker")

        self._chunker = chunker
        self._selector = selector or SummarizationStrategySelector()
        self._profiler = profiler or DocumentProfiler(
            token_counter=self._chunker.token_counter
        )
        self._intent_classifier = intent_classifier or IntentClassifier()
        self._adaptive_planner = adaptive_planner or AdaptiveStrategyPlanner()

    @property
    def chunker(self) -> TextChunker:
        return self._chunker

    @property
    def selector(self) -> SummarizationStrategySelector:
        return self._selector

    @property
    def profiler(self) -> DocumentProfiler:
        return self._profiler

    @property
    def intent_classifier(self) -> IntentClassifier:
        return self._intent_classifier

    @property
    def adaptive_planner(self) -> AdaptiveStrategyPlanner:
        return self._adaptive_planner

    def plan(
        self,
        text: str,
        *,
        intent: SummarizationIntent | str | None = None,
    ) -> SummarizationPlan:
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

        adaptive = self._adaptive_planner.decide(
            selection,
            profile,
            intent_classification.intent,
        )

        final_selection = selection
        if adaptive.promoted:
            final_selection = StrategySelection(
                strategy=adaptive.selected_strategy,
                token_count=selection.token_count,
                chunk_count=selection.chunk_count,
                reason=f"{selection.reason}; {adaptive.reasons[0]}",
                metadata={
                    **selection.metadata,
                    "baseline_strategy": selection.strategy.value,
                    "adaptive_strategy": adaptive.selected_strategy.value,
                    "adaptive_planner_version": adaptive.metadata["planner_version"],
                },
            )

        return SummarizationPlan(
            strategy=adaptive.selected_strategy,
            selection=final_selection,
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
                "strategy_reason": final_selection.reason,
                "structure_type": profile.structure_type.value,
                "paragraph_count": profile.paragraph_count,
                "sentence_count": profile.sentence_count,
                "intent": intent_classification.intent.value,
                "intent_confidence": intent_classification.confidence,
                "intent_explicit": intent_classification.explicit,
                "intent_matches": intent_classification.matched_terms,
                "baseline_strategy": selection.strategy.value,
                "adaptive_strategy": adaptive.selected_strategy.value,
                "adaptive_promoted": adaptive.promoted,
                "adaptive_reasons": adaptive.reasons,
                "adaptive_signals": adaptive.signals,
            },
        )

    @staticmethod
    def _digest(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
