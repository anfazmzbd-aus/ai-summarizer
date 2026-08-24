"""
V10 M7 integration explainability and safety boundary.

Produces an immutable audit representation of the complete M7
intelligence-to-execution integration path.

M7.6 adds no execution authority and performs no runtime actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .adaptation_decision import AdaptationDisposition
from .execution_integration import (
    ExecutionIntegrationDirective,
    ExecutionIntegrationMode,
)
from .intelligence_orchestration_handoff import (
    IntelligenceOrchestrationHandoff,
)
from .orchestration_directive import (
    OrchestrationDisposition,
)
from .orchestration_directive_guard import (
    DirectiveValidationStatus,
)
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class IntegrationExplanation:
    """
    Immutable audit trace for one M7 integration result.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    adaptation_disposition: AdaptationDisposition
    orchestration_disposition: OrchestrationDisposition
    validation_status: DirectiveValidationStatus
    integration_mode: ExecutionIntegrationMode

    execution_authorized: bool
    bounded_constraint_required: bool
    review_required: bool

    orchestration_reasons: tuple[str, ...]
    validation_reasons: tuple[str, ...]
    integration_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.adaptation_disposition,
            AdaptationDisposition,
        ):
            raise TypeError(
                "adaptation_disposition must be an " "AdaptationDisposition"
            )

        if not isinstance(
            self.orchestration_disposition,
            OrchestrationDisposition,
        ):
            raise TypeError(
                "orchestration_disposition must be an " "OrchestrationDisposition"
            )

        if not isinstance(
            self.validation_status,
            DirectiveValidationStatus,
        ):
            raise TypeError("validation_status must be a " "DirectiveValidationStatus")

        if not isinstance(
            self.integration_mode,
            ExecutionIntegrationMode,
        ):
            raise TypeError("integration_mode must be an " "ExecutionIntegrationMode")

        for name, value in {
            "execution_authorized": self.execution_authorized,
            "bounded_constraint_required": (self.bounded_constraint_required),
            "review_required": self.review_required,
        }.items():
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be a bool")

        for field_name, reasons in (
            (
                "orchestration_reasons",
                self.orchestration_reasons,
            ),
            (
                "validation_reasons",
                self.validation_reasons,
            ),
            (
                "integration_reasons",
                self.integration_reasons,
            ),
        ):
            if not isinstance(reasons, tuple):
                raise TypeError(f"{field_name} must be a tuple")

            for reason in reasons:
                if not isinstance(reason, str):
                    raise TypeError(f"{field_name} must contain strings")


class IntegrationExplanationBuilder:
    """Build one deterministic M7 integration audit trace."""

    def build(
        self,
        handoff: IntelligenceOrchestrationHandoff,
        integration: ExecutionIntegrationDirective,
    ) -> IntegrationExplanation:
        """Build a validated integration explanation."""

        if not isinstance(
            handoff,
            IntelligenceOrchestrationHandoff,
        ):
            raise TypeError("handoff must be an " "IntelligenceOrchestrationHandoff")

        if not isinstance(
            integration,
            ExecutionIntegrationDirective,
        ):
            raise TypeError("integration must be an " "ExecutionIntegrationDirective")

        self._validate_chain(
            handoff=handoff,
            integration=integration,
        )

        return IntegrationExplanation(
            context_id=handoff.context_id,
            correlation_id=handoff.correlation_id,
            action=handoff.action,
            adaptation_disposition=(handoff.directive.adaptation_disposition),
            orchestration_disposition=(handoff.orchestration_disposition),
            validation_status=handoff.validation.status,
            integration_mode=integration.mode,
            execution_authorized=(integration.execution_change_authorized),
            bounded_constraint_required=(integration.bounded_constraint_required),
            review_required=integration.review_required,
            orchestration_reasons=handoff.directive.reasons,
            validation_reasons=handoff.validation.reasons,
            integration_reasons=integration.reasons,
        )

    @staticmethod
    def _validate_chain(
        *,
        handoff: IntelligenceOrchestrationHandoff,
        integration: ExecutionIntegrationDirective,
    ) -> None:
        if integration.context_id != handoff.context_id:
            raise ValueError("integration context_id must match handoff")

        if integration.correlation_id != handoff.correlation_id:
            raise ValueError("integration correlation_id must match handoff")

        if integration.action is not handoff.action:
            raise ValueError("integration action must match handoff")

        if handoff.validation.status is not DirectiveValidationStatus.VALID:
            raise ValueError(
                "integration explanation requires valid " "directive validation"
            )

        if integration.execution_change_authorized is not handoff.execution_authorized:
            raise ValueError("integration execution authority must match handoff")

        if integration.review_required is not handoff.review_required:
            raise ValueError("integration review requirement must match handoff")


__all__ = [
    "IntegrationExplanation",
    "IntegrationExplanationBuilder",
]
