"""
V10 intelligent orchestration coordinator.

The IntelligenceOrchestrator converts an immutable IntelligenceContext
into a provider-independent TaskDecision.

The orchestrator owns decision policy only.

It does not:
- execute tasks
- select providers
- invoke LLMs
- create runtime objects
- modify V9.3 planning components
"""

from __future__ import annotations

from dataclasses import dataclass

from app.summarization.intelligence import SummarizationIntent

from .context import IntelligenceContext
from .task_decision import TaskAction, TaskDecision


@dataclass(frozen=True, slots=True)
class IntelligenceOrchestrator:
    """
    Determine the next orchestration action from V10 intelligence context.

    The policy is intentionally deterministic. The same context produces
    the same decision when its supplied intelligence and constraints are
    unchanged.
    """

    def decide(
        self,
        context: IntelligenceContext,
    ) -> TaskDecision:
        """
        Produce the next provider-independent task decision.

        The method performs no execution and has no provider dependency.
        """
        if not isinstance(context, IntelligenceContext):
            raise TypeError("context must be an IntelligenceContext")

        action, reason, confidence = self._determine_action(context)

        return TaskDecision.create(
            action=action,
            context_id=context.context_id,
            correlation_id=context.correlation_id,
            reason=reason,
            confidence=confidence,
        )

    @staticmethod
    def _determine_action(
        context: IntelligenceContext,
    ) -> tuple[TaskAction, str, float]:
        """
        Determine the next task using the strongest available signal.

        Explicit constraints have precedence over inferred intent.
        Intent then provides the primary V9.3 intelligence signal.
        A context without intelligence defaults to summarization.
        """
        constraints = context.constraints

        if constraints.get("abort") is True:
            return (
                TaskAction.ABORT,
                "orchestration aborted by constraint",
                1.0,
            )

        if constraints.get("retry") is True:
            return (
                TaskAction.RETRY,
                "retry requested by constraint",
                1.0,
            )

        if constraints.get("fallback") is True:
            return (
                TaskAction.FALLBACK,
                "fallback requested by constraint",
                1.0,
            )

        if constraints.get("verify") is True:
            return (
                TaskAction.VERIFY,
                "verification requested by constraint",
                1.0,
            )

        if constraints.get("retrieve") is True:
            return (
                TaskAction.RETRIEVE,
                "retrieval requested by constraint",
                1.0,
            )

        if constraints.get("refine") is True:
            return (
                TaskAction.REFINE,
                "refinement requested by constraint",
                1.0,
            )

        intent = context.intent

        if intent is None:
            return (
                TaskAction.SUMMARIZE,
                "no explicit intelligence signal; default summarization",
                1.0,
            )

        if intent is SummarizationIntent.GENERAL:
            return (
                TaskAction.SUMMARIZE,
                "general summarization intent",
                1.0,
            )

        if intent is SummarizationIntent.EXECUTIVE:
            return (
                TaskAction.SUMMARIZE,
                "executive summarization intent",
                1.0,
            )

        if intent is SummarizationIntent.ACTION_ITEMS:
            return (
                TaskAction.SUMMARIZE,
                "action-items summarization intent",
                1.0,
            )

        if intent is SummarizationIntent.KEY_POINTS:
            return (
                TaskAction.SUMMARIZE,
                "key-points summarization intent",
                1.0,
            )

        if intent is SummarizationIntent.FINDINGS:
            return (
                TaskAction.SUMMARIZE,
                "findings summarization intent",
                1.0,
            )

        if intent is SummarizationIntent.INSIGHTS:
            return (
                TaskAction.SUMMARIZE,
                "insights summarization intent",
                1.0,
            )

        if intent is SummarizationIntent.TECHNICAL:
            return (
                TaskAction.SUMMARIZE,
                "technical summarization intent",
                1.0,
            )

        return (
            TaskAction.SUMMARIZE,
            "unrecognized intent; default summarization",
            0.5,
        )


__all__ = ["IntelligenceOrchestrator"]
