"""
V10 planner outcome contract.

Provides a stable, provider-independent representation of the result produced
by the V9.3 planning boundary.

The outcome does not replace or mutate the V9.3 SummarizationPlan.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from app.summarization.planning.models import SummarizationPlan
from app.summarization.strategies.models import SummarizationStrategyType

from .strategy_policy_result import StrategyPolicyResult
from .task_decision import TaskDecision


@dataclass(frozen=True, slots=True)
class PlannerOutcome:
    """
    Immutable V10 representation of a completed planning decision.

    The V9.3 plan remains the authoritative planning artifact. This object
    provides normalized feedback for the V10 intelligence and orchestration
    layers.
    """

    plan: SummarizationPlan
    task_decision: TaskDecision
    strategy_policy_result: StrategyPolicyResult
    selected_strategy: SummarizationStrategyType
    decision_reason: str
    constraint_summary: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if not isinstance(self.plan, SummarizationPlan):
            raise TypeError("plan must be a SummarizationPlan")

        if not isinstance(self.task_decision, TaskDecision):
            raise TypeError("task_decision must be a TaskDecision")

        if not isinstance(
            self.strategy_policy_result,
            StrategyPolicyResult,
        ):
            raise TypeError("strategy_policy_result must be a StrategyPolicyResult")

        if self.strategy_policy_result.plan is not self.plan:
            raise ValueError(
                "plan must be the plan contained in strategy_policy_result"
            )

        if not isinstance(
            self.selected_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("selected_strategy must be a SummarizationStrategyType")

        if self.selected_strategy is not self.plan.strategy:
            raise ValueError("selected_strategy must match plan.strategy")

        if self.selected_strategy is not self.strategy_policy_result.selected_strategy:
            raise ValueError("selected_strategy must match strategy_policy_result")

        if not isinstance(self.decision_reason, str):
            raise TypeError("decision_reason must be a string")

        if not isinstance(self.constraint_summary, tuple):
            raise TypeError("constraint_summary must be a tuple")

        if any(not isinstance(item, str) for item in self.constraint_summary):
            raise TypeError("constraint_summary must contain only strings")

        if self.metadata is None:
            metadata: Mapping[str, Any] = {}
        elif isinstance(self.metadata, Mapping):
            metadata = self.metadata
        else:
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    @property
    def context_id(self) -> UUID:
        """Return the originating intelligence context identifier."""
        return self.strategy_policy_result.context_id

    @property
    def correlation_id(self) -> UUID:
        """Return the originating correlation identifier."""
        return self.strategy_policy_result.correlation_id

    @property
    def request_id(self) -> str:
        """Return the request identifier from the intelligence context."""
        return self.task_decision.metadata.get("request_id", "")

    @property
    def preference_satisfied(self) -> bool | None:
        """Return the V10 strategy preference outcome."""
        return self.strategy_policy_result.preference_satisfied

    @property
    def preference_overridden(self) -> bool:
        """Return whether V9.3 selected a strategy different from the preference."""
        return self.strategy_policy_result.preference_overridden

    @property
    def planner_metadata(self) -> Mapping[str, Any]:
        """Return the original V9.3 planner metadata."""
        return MappingProxyType(dict(self.plan.metadata))

    @property
    def source_digest(self) -> str:
        """Return the deterministic source digest from the V9.3 plan."""
        return self.plan.source_digest

    @property
    def token_count(self) -> int:
        """Return the planned token count."""
        return self.plan.token_count

    @property
    def chunk_count(self) -> int:
        """Return the planned chunk count."""
        return self.plan.chunk_count


__all__ = ["PlannerOutcome"]
