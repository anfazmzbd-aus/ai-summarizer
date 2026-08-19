"""
V10 strategy policy evaluation result.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.summarization.strategies.models import SummarizationStrategyType

from .planner_handoff import PlannerHandoffResult
from .strategy_policy import StrategyHandoffPolicy


@dataclass(frozen=True, slots=True)
class StrategyPolicyResult:
    """
    Immutable result of applying a strategy policy to a V9.3 plan.

    The underlying V9.3 plan remains unchanged.
    """

    handoff: PlannerHandoffResult
    policy: StrategyHandoffPolicy
    selected_strategy: SummarizationStrategyType
    preference_satisfied: bool | None

    def __post_init__(self) -> None:
        if not isinstance(self.handoff, PlannerHandoffResult):
            raise TypeError("handoff must be a PlannerHandoffResult")

        if not isinstance(self.policy, StrategyHandoffPolicy):
            raise TypeError("policy must be a StrategyHandoffPolicy")

        if not isinstance(
            self.selected_strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("selected_strategy must be a SummarizationStrategyType")

        if self.preference_satisfied is not None and not isinstance(
            self.preference_satisfied,
            bool,
        ):
            raise TypeError("preference_satisfied must be a boolean or None")

    @property
    def plan(self):
        """Return the unchanged V9.3 summarization plan."""
        return self.handoff.plan

    @property
    def context_id(self):
        """Return the V10 context identifier."""
        return self.handoff.context_id

    @property
    def correlation_id(self):
        """Return the V10 correlation identifier."""
        return self.handoff.correlation_id

    @property
    def preference_overridden(self) -> bool:
        """
        Return whether V9.3 selected a strategy different from the preference.
        """
        return self.preference_satisfied is False


__all__ = ["StrategyPolicyResult"]
