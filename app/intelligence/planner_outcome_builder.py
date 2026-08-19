"""
V10 planner outcome builder.

Converts the existing strategy-policy handoff result into the stable V10
PlannerOutcome contract.
"""

from __future__ import annotations

from typing import Any, Mapping

from .planner_outcome import PlannerOutcome
from .strategy_policy_result import StrategyPolicyResult
from .task_decision import TaskDecision


class PlannerOutcomeBuilder:
    """
    Build a normalized V10 planner outcome from an existing strategy-policy
    result.

    This class contains no planning logic and does not modify the V9.3 plan.
    """

    def build(
        self,
        *,
        result: StrategyPolicyResult,
        task_decision: TaskDecision,
        metadata: Mapping[str, Any] | None = None,
    ) -> PlannerOutcome:
        """
        Build a PlannerOutcome from the completed planning handoff.
        """
        if not isinstance(result, StrategyPolicyResult):
            raise TypeError("result must be a StrategyPolicyResult")

        if not isinstance(task_decision, TaskDecision):
            raise TypeError("task_decision must be a TaskDecision")

        plan = result.plan

        decision_reason = self._decision_reason(
            result=result,
            task_decision=task_decision,
        )

        constraint_summary = self._constraint_summary(result)

        return PlannerOutcome(
            plan=plan,
            task_decision=task_decision,
            strategy_policy_result=result,
            selected_strategy=result.selected_strategy,
            decision_reason=decision_reason,
            constraint_summary=constraint_summary,
            metadata={} if metadata is None else metadata,
        )

    @staticmethod
    def _decision_reason(
        *,
        result: StrategyPolicyResult,
        task_decision: TaskDecision,
    ) -> str:
        """
        Resolve the normalized decision reason.

        The V9.3 planner's strategy rationale remains authoritative when
        available. The V10 task decision provides the orchestration-level
        reason.
        """
        strategy_reason = result.plan.metadata.get("strategy_reason")

        if isinstance(strategy_reason, str) and strategy_reason:
            return strategy_reason

        if task_decision.reason:
            return task_decision.reason

        return ""

    @staticmethod
    def _constraint_summary(
        result: StrategyPolicyResult,
    ) -> tuple[str, ...]:
        """
        Produce deterministic summaries of the V10 strategy constraints.
        """
        policy = result.policy
        summary: list[str] = []

        if policy.preferred_strategy is not None:
            summary.append(f"preferred_strategy={policy.preferred_strategy.value}")

        if policy.allowed_strategies:
            allowed = ",".join(strategy.value for strategy in policy.allowed_strategies)
            summary.append(f"allowed_strategies={allowed}")

        if policy.required_strategy is not None:
            summary.append(f"required_strategy={policy.required_strategy.value}")

        return tuple(summary)


__all__ = ["PlannerOutcomeBuilder"]
