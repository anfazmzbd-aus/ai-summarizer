"""
V10 constraint-aware planner handoff.

Applies V10 planning constraints around the existing V9.3 planner without
changing the V9.3 planning implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.summarization.planning import SummarizationPlan

from .context import IntelligenceContext
from .planner_handoff import PlannerHandoff, PlannerHandoffResult
from .planning_constraints import PlanningConstraints
from .task_decision import TaskDecision


@dataclass(frozen=True, slots=True)
class ConstraintAwarePlannerHandoff:
    """
    Apply V10 planning constraints around PlannerHandoff.

    Constraints are validated at the V10 boundary. The underlying V9.3
    planner remains responsible for chunking and strategy selection.
    """

    handoff: PlannerHandoff

    def execute(
        self,
        *,
        text: str,
        context: IntelligenceContext,
        decision: TaskDecision,
    ) -> PlannerHandoffResult:
        """
        Produce a V9.3 plan and validate it against V10 constraints.
        """
        constraints = PlanningConstraints.from_mapping(context.constraints)

        self._validate_input_budget(
            context=context,
            constraints=constraints,
        )

        result = self.handoff.handoff(
            text=text,
            context=context,
            decision=decision,
        )

        self._validate_plan(
            plan=result.plan,
            constraints=constraints,
        )

        return result

    @staticmethod
    def _validate_input_budget(
        *,
        context: IntelligenceContext,
        constraints: PlanningConstraints,
    ) -> None:
        if constraints.max_input_tokens is None:
            return

        profile = context.document_profile

        if profile is None:
            return

        if profile.token_count > constraints.max_input_tokens:
            raise ValueError(
                "document token count exceeds max_input_tokens: "
                f"{profile.token_count} > {constraints.max_input_tokens}"
            )

    @staticmethod
    def _validate_plan(
        *,
        plan: SummarizationPlan,
        constraints: PlanningConstraints,
    ) -> None:
        if (
            constraints.max_input_tokens is not None
            and plan.token_count > constraints.max_input_tokens
        ):
            raise ValueError(
                "plan token count exceeds max_input_tokens: "
                f"{plan.token_count} > {constraints.max_input_tokens}"
            )

        if (
            constraints.max_chunks is not None
            and plan.chunk_count > constraints.max_chunks
        ):
            raise ValueError(
                "plan chunk count exceeds max_chunks: "
                f"{plan.chunk_count} > {constraints.max_chunks}"
            )

        if (
            constraints.allowed_strategies
            and plan.strategy not in constraints.allowed_strategies
        ):
            allowed = ", ".join(
                strategy.value for strategy in constraints.allowed_strategies
            )

            raise ValueError(
                f"selected strategy '{plan.strategy.value}' is not allowed; "
                f"allowed strategies: {allowed}"
            )

        if (
            constraints.required_strategy is not None
            and plan.strategy is not constraints.required_strategy
        ):
            raise ValueError(
                "selected strategy does not satisfy required_strategy: "
                f"{plan.strategy.value} != "
                f"{constraints.required_strategy.value}"
            )


__all__ = ["ConstraintAwarePlannerHandoff"]
