"""
V10 strategy-policy-aware planner handoff.

The existing V9.3 planner remains responsible for selecting the strategy.
This layer evaluates the resulting selection against V10 strategy policy.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constraint_handoff import ConstraintAwarePlannerHandoff
from .context import IntelligenceContext
from .strategy_policy import StrategyHandoffPolicy
from .strategy_policy_result import StrategyPolicyResult
from .task_decision import TaskDecision


@dataclass(frozen=True, slots=True)
class StrategyPolicyHandoff:
    """
    Apply V10 strategy policy around the existing constraint-aware handoff.
    """

    handoff: ConstraintAwarePlannerHandoff

    def execute(
        self,
        *,
        text: str,
        context: IntelligenceContext,
        decision: TaskDecision,
    ) -> StrategyPolicyResult:
        """
        Produce a V9.3 plan and evaluate its strategy against V10 policy.
        """
        policy = StrategyHandoffPolicy.from_mapping(context.constraints)

        result = self.handoff.execute(
            text=text,
            context=context,
            decision=decision,
        )

        selected_strategy = result.plan.strategy

        self._validate_allowed_strategy(
            selected_strategy=selected_strategy,
            policy=policy,
        )

        self._validate_required_strategy(
            selected_strategy=selected_strategy,
            policy=policy,
        )

        preference_satisfied = self._evaluate_preference(
            selected_strategy=selected_strategy,
            policy=policy,
        )

        return StrategyPolicyResult(
            handoff=result,
            policy=policy,
            selected_strategy=selected_strategy,
            preference_satisfied=preference_satisfied,
        )

    @staticmethod
    def _validate_allowed_strategy(
        *,
        selected_strategy,
        policy: StrategyHandoffPolicy,
    ) -> None:
        if not policy.allowed_strategies:
            return

        if selected_strategy not in policy.allowed_strategies:
            allowed = ", ".join(
                strategy.value for strategy in policy.allowed_strategies
            )

            raise ValueError(
                f"selected strategy '{selected_strategy.value}' is not allowed; "
                f"allowed strategies: {allowed}"
            )

    @staticmethod
    def _validate_required_strategy(
        *,
        selected_strategy,
        policy: StrategyHandoffPolicy,
    ) -> None:
        if policy.required_strategy is None:
            return

        if selected_strategy is not policy.required_strategy:
            raise ValueError(
                "selected strategy does not satisfy required_strategy: "
                f"{selected_strategy.value} != "
                f"{policy.required_strategy.value}"
            )

    @staticmethod
    def _evaluate_preference(
        *,
        selected_strategy,
        policy: StrategyHandoffPolicy,
    ) -> bool | None:
        if policy.preferred_strategy is None:
            return None

        return selected_strategy is policy.preferred_strategy


__all__ = ["StrategyPolicyHandoff"]
