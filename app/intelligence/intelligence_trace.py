"""
V10 M8 intelligence trace contract.

Defines the immutable observability representation spanning decision,
adaptation, and execution-integration explanation layers.

M8.1 defines representation only. It does not validate cross-stage
provenance, derive observability status, generate diagnostics, or modify
intelligence behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .adaptation_explanation import AdaptationExplanation
from .decision_explanation import DecisionExplanation
from .integration_explanation import IntegrationExplanation
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class IntelligenceTrace:
    """
    Immutable intelligence lifecycle trace.

    The trace preserves existing explanation contracts and exposes compact
    lifecycle state for later observability processing.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    decision_explanation: DecisionExplanation
    adaptation_explanation: AdaptationExplanation
    integration_explanation: IntegrationExplanation

    historical_influence_applied: bool
    adaptation_applied: bool
    execution_authorized: bool
    review_required: bool

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.decision_explanation,
            DecisionExplanation,
        ):
            raise TypeError("decision_explanation must be a DecisionExplanation")

        if not isinstance(
            self.adaptation_explanation,
            AdaptationExplanation,
        ):
            raise TypeError(
                "adaptation_explanation must be an " "AdaptationExplanation"
            )

        if not isinstance(
            self.integration_explanation,
            IntegrationExplanation,
        ):
            raise TypeError(
                "integration_explanation must be an " "IntegrationExplanation"
            )

        boolean_fields = {
            "historical_influence_applied": (self.historical_influence_applied),
            "adaptation_applied": self.adaptation_applied,
            "execution_authorized": self.execution_authorized,
            "review_required": self.review_required,
        }

        for name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be a bool")


__all__ = ["IntelligenceTrace"]
