"""
V9.3-M4 deterministic adaptive strategy planner.

This layer consumes the existing V9.2 strategy selection and V9.3
document-intelligence signals. It never changes the V9.2 selector.
"""

from __future__ import annotations

from app.summarization.intelligence import (
    DocumentProfile,
    DocumentStructureType,
    SummarizationIntent,
)
from app.summarization.strategies.models import (
    StrategySelection,
    SummarizationStrategyType,
)

from .adaptive_models import AdaptiveStrategyDecision


class AdaptiveStrategyPlanner:
    """Apply conservative, deterministic strategy adaptations."""

    planner_version = "v9.3-m4"

    _PROMOTION_INTENTS = frozenset(
        {
            SummarizationIntent.ACTION_ITEMS,
            SummarizationIntent.FINDINGS,
            SummarizationIntent.INSIGHTS,
            SummarizationIntent.TECHNICAL,
        }
    )

    _PROMOTION_STRUCTURES = frozenset(
        {
            DocumentStructureType.STRUCTURED,
            DocumentStructureType.CODE,
            DocumentStructureType.MIXED,
        }
    )

    def decide(
        self,
        selection: StrategySelection,
        profile: DocumentProfile,
        intent: SummarizationIntent,
    ) -> AdaptiveStrategyDecision:
        """Return a deterministic adaptive decision."""
        if not isinstance(selection, StrategySelection):
            raise TypeError("selection must be a StrategySelection")
        if not isinstance(profile, DocumentProfile):
            raise TypeError("profile must be a DocumentProfile")
        if not isinstance(intent, SummarizationIntent):
            raise TypeError("intent must be a SummarizationIntent")

        baseline = selection.strategy

        if baseline is SummarizationStrategyType.HIERARCHICAL:
            return self._retain(
                baseline,
                "hierarchical baseline is retained",
                signals=("baseline_hierarchical",),
            )

        if baseline is SummarizationStrategyType.MAP_REDUCE:
            return self._retain(
                baseline,
                "map-reduce baseline is retained",
                signals=("baseline_map_reduce",),
            )

        signals: list[str] = []
        reasons: list[str] = []

        if profile.structure_type in self._PROMOTION_STRUCTURES:
            signals.append(f"structure:{profile.structure_type.value}")
            reasons.append("document structure benefits from multi-stage summarization")

        if intent in self._PROMOTION_INTENTS:
            signals.append(f"intent:{intent.value}")
            reasons.append("summarization intent benefits from chunk-level synthesis")

        if profile.paragraph_count > 1:
            signals.append("multiple_paragraphs")

        # Direct execution is retained for empty and single-chunk documents.
        if selection.chunk_count <= 1:
            return self._retain(
                baseline,
                "direct baseline retained for a single chunk",
                signals=("single_chunk",),
            )

        if signals:
            return AdaptiveStrategyDecision(
                baseline_strategy=baseline,
                selected_strategy=SummarizationStrategyType.MAP_REDUCE,
                promoted=True,
                reasons=tuple(dict.fromkeys(reasons)),
                signals=tuple(dict.fromkeys(signals)),
                metadata={
                    "planner_version": self.planner_version,
                    "promotion": "direct_to_map_reduce",
                },
            )

        return self._retain(
            baseline,
            "no adaptive signal exceeded the promotion threshold",
            signals=("no_promotion_signal",),
        )

    def _retain(
        self,
        strategy: SummarizationStrategyType,
        reason: str,
        *,
        signals: tuple[str, ...],
    ) -> AdaptiveStrategyDecision:
        return AdaptiveStrategyDecision(
            baseline_strategy=strategy,
            selected_strategy=strategy,
            promoted=False,
            reasons=(reason,),
            signals=signals,
            metadata={
                "planner_version": self.planner_version,
                "promotion": None,
            },
        )


__all__ = ["AdaptiveStrategyPlanner"]
