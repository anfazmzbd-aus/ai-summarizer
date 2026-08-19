"""
V10 planner decision feedback contract.

Represents the information returned from planning to the intelligence
orchestration layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from app.summarization.strategies.models import SummarizationStrategyType

from .planner_outcome import PlannerOutcome


@dataclass(frozen=True, slots=True)
class DecisionFeedback:
    """
    Immutable feedback produced after planner evaluation.

    This contract intentionally contains decision-level information rather
    than execution-level information.
    """

    context_id: UUID
    correlation_id: UUID
    selected_strategy: SummarizationStrategyType
    decision_reason: str
    preference_satisfied: bool | None
    hard_constraints_satisfied: bool
    constraint_summary: tuple[str, ...]
    source_digest: str
    token_count: int
    chunk_count: int
    metadata: Mapping[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(
            self.selected_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("selected_strategy must be a SummarizationStrategyType")

        if not isinstance(self.decision_reason, str):
            raise TypeError("decision_reason must be a string")

        if self.preference_satisfied is not None and not isinstance(
            self.preference_satisfied,
            bool,
        ):
            raise TypeError("preference_satisfied must be a boolean or None")

        if not isinstance(
            self.hard_constraints_satisfied,
            bool,
        ):
            raise TypeError("hard_constraints_satisfied must be a boolean")

        if not isinstance(self.constraint_summary, tuple):
            raise TypeError("constraint_summary must be a tuple")

        if not isinstance(self.source_digest, str):
            raise TypeError("source_digest must be a string")

        if not isinstance(self.token_count, int):
            raise TypeError("token_count must be an integer")

        if not isinstance(self.chunk_count, int):
            raise TypeError("chunk_count must be an integer")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        if self.chunk_count < 0:
            raise ValueError("chunk_count must be non-negative")

        metadata = {} if self.metadata is None else self.metadata

        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    @classmethod
    def from_outcome(
        cls,
        outcome: PlannerOutcome,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> "DecisionFeedback":
        """
        Build feedback directly from a PlannerOutcome.
        """
        if not isinstance(outcome, PlannerOutcome):
            raise TypeError("outcome must be a PlannerOutcome")

        return cls(
            context_id=outcome.context_id,
            correlation_id=outcome.correlation_id,
            selected_strategy=outcome.selected_strategy,
            decision_reason=outcome.decision_reason,
            preference_satisfied=outcome.preference_satisfied,
            hard_constraints_satisfied=True,
            constraint_summary=outcome.constraint_summary,
            source_digest=outcome.source_digest,
            token_count=outcome.token_count,
            chunk_count=outcome.chunk_count,
            metadata={} if metadata is None else metadata,
        )


__all__ = ["DecisionFeedback"]
