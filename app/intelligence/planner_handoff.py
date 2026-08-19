"""
V10 planner handoff boundary.

Translates a V10 TaskDecision and IntelligenceContext into a call to the
existing V9.3 SummarizationPlanner.

The handoff owns boundary validation and provenance preservation only.

It does not:
- implement summarization planning
- select summarization strategies
- chunk documents
- execute summarization
- invoke providers
- modify the V9.3 planner
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.summarization.planning import SummarizationPlan, SummarizationPlanner

from .context import IntelligenceContext
from .task_decision import TaskAction, TaskDecision


@dataclass(frozen=True, slots=True)
class PlannerHandoffResult:
    """
    Result of handing a V10 task decision to the V9.3 planner.

    The V9.3 SummarizationPlan is preserved unchanged. V10 provenance is
    carried alongside the plan rather than injected into the V9.3 model.
    """

    plan: SummarizationPlan
    context_id: Any
    correlation_id: Any

    def __post_init__(self) -> None:
        if not isinstance(self.plan, SummarizationPlan):
            raise TypeError("plan must be a SummarizationPlan")

    @property
    def provenance(self) -> dict[str, str]:
        """Return the V10 provenance identifiers for the handoff."""
        return {
            "context_id": str(self.context_id),
            "correlation_id": str(self.correlation_id),
        }


class PlannerHandoff:
    """
    Boundary adapter between V10 orchestration and the V9.3 planner.

    Only TaskAction.SUMMARIZE is currently supported because the existing
    SummarizationPlanner is specifically a summarization planning component.
    Other V10 task actions belong to future orchestration domains.
    """

    def __init__(self, planner: SummarizationPlanner) -> None:
        if not isinstance(planner, SummarizationPlanner):
            raise TypeError("planner must be a SummarizationPlanner")

        self._planner = planner

    @property
    def planner(self) -> SummarizationPlanner:
        """Return the configured V9.3 planner."""
        return self._planner

    def handoff(
        self,
        *,
        text: str,
        context: IntelligenceContext,
        decision: TaskDecision,
    ) -> PlannerHandoffResult:
        """
        Hand a V10 summarization decision to the existing V9.3 planner.

        The source text is supplied at the application boundary and is never
        stored in the V10 intelligence contracts.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not isinstance(context, IntelligenceContext):
            raise TypeError("context must be an IntelligenceContext")

        if not isinstance(decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        self._validate_provenance(context, decision)
        self._validate_action(decision)

        plan = self._planner.plan(
            text,
            intent=context.intent,
        )

        return PlannerHandoffResult(
            plan=plan,
            context_id=context.context_id,
            correlation_id=context.correlation_id,
        )

    @staticmethod
    def _validate_provenance(
        context: IntelligenceContext,
        decision: TaskDecision,
    ) -> None:
        if decision.context_id != context.context_id:
            raise ValueError(
                "task decision context_id does not match intelligence context"
            )

        if decision.correlation_id != context.correlation_id:
            raise ValueError(
                "task decision correlation_id does not match intelligence context"
            )

    @staticmethod
    def _validate_action(decision: TaskDecision) -> None:
        if decision.action is not TaskAction.SUMMARIZE:
            raise ValueError(
                "only TaskAction.SUMMARIZE can be handed to the " "SummarizationPlanner"
            )


__all__ = ["PlannerHandoff", "PlannerHandoffResult"]
