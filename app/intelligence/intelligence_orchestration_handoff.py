"""
V10 M7 intelligence-to-orchestration handoff contract.

Composes the bounded adaptive policy outcome, translated orchestration
directive, and independent guard validation into one immutable handoff
for later execution integration.

M7.4 performs composition and consistency validation only.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .adaptive_policy_outcome import AdaptivePolicyOutcome
from .orchestration_directive import (
    OrchestrationDirective,
    OrchestrationDisposition,
)
from .orchestration_directive_guard import (
    DirectiveValidationStatus,
    OrchestrationDirectiveValidation,
)
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class IntelligenceOrchestrationHandoff:
    """Immutable validated handoff from intelligence to orchestration."""

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    adaptive_outcome: AdaptivePolicyOutcome
    directive: OrchestrationDirective
    validation: OrchestrationDirectiveValidation

    orchestration_disposition: OrchestrationDisposition
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
            self.adaptive_outcome,
            AdaptivePolicyOutcome,
        ):
            raise TypeError("adaptive_outcome must be an AdaptivePolicyOutcome")

        if not isinstance(
            self.directive,
            OrchestrationDirective,
        ):
            raise TypeError("directive must be an OrchestrationDirective")

        if not isinstance(
            self.validation,
            OrchestrationDirectiveValidation,
        ):
            raise TypeError("validation must be an " "OrchestrationDirectiveValidation")

        if not isinstance(
            self.orchestration_disposition,
            OrchestrationDisposition,
        ):
            raise TypeError(
                "orchestration_disposition must be an " "OrchestrationDisposition"
            )

        if not isinstance(self.execution_authorized, bool):
            raise TypeError("execution_authorized must be a bool")

        if not isinstance(self.review_required, bool):
            raise TypeError("review_required must be a bool")

        self._validate_consistency()

    def _validate_consistency(self) -> None:
        if self.context_id != self.adaptive_outcome.context_id:
            raise ValueError("context_id must match adaptive_outcome")

        if self.correlation_id != self.adaptive_outcome.correlation_id:
            raise ValueError("correlation_id must match adaptive_outcome")

        if self.action is not self.adaptive_outcome.action:
            raise ValueError("action must match adaptive_outcome")

        if self.directive.context_id != self.context_id:
            raise ValueError("directive context_id must match handoff")

        if self.directive.correlation_id != self.correlation_id:
            raise ValueError("directive correlation_id must match handoff")

        if self.directive.action is not self.action:
            raise ValueError("directive action must match handoff")

        if (
            self.directive.adaptation_disposition
            is not self.adaptive_outcome.adaptation_disposition
        ):
            raise ValueError(
                "directive adaptation_disposition must match " "adaptive_outcome"
            )

        if self.validation.directive != self.directive:
            raise ValueError("validation directive must match handoff directive")

        if self.validation.status is not DirectiveValidationStatus.VALID:
            raise ValueError("handoff requires a valid directive validation")

        if (
            self.orchestration_disposition
            is not self.directive.orchestration_disposition
        ):
            raise ValueError("orchestration_disposition must match directive")

        if self.execution_authorized is not self.validation.execution_authorized:
            raise ValueError("execution_authorized must match validation")

        if self.review_required is not self.validation.review_required:
            raise ValueError("review_required must match validation")


class IntelligenceOrchestrationHandoffBoundary:
    """Compose a validated intelligence-to-orchestration handoff."""

    def compose(
        self,
        adaptive_outcome: AdaptivePolicyOutcome,
        directive: OrchestrationDirective,
        validation: OrchestrationDirectiveValidation,
    ) -> IntelligenceOrchestrationHandoff:
        """Compose one validated handoff."""

        if not isinstance(
            adaptive_outcome,
            AdaptivePolicyOutcome,
        ):
            raise TypeError("adaptive_outcome must be an AdaptivePolicyOutcome")

        if not isinstance(
            directive,
            OrchestrationDirective,
        ):
            raise TypeError("directive must be an OrchestrationDirective")

        if not isinstance(
            validation,
            OrchestrationDirectiveValidation,
        ):
            raise TypeError("validation must be an " "OrchestrationDirectiveValidation")

        return IntelligenceOrchestrationHandoff(
            context_id=adaptive_outcome.context_id,
            correlation_id=adaptive_outcome.correlation_id,
            action=adaptive_outcome.action,
            adaptive_outcome=adaptive_outcome,
            directive=directive,
            validation=validation,
            orchestration_disposition=(directive.orchestration_disposition),
            execution_authorized=(validation.execution_authorized),
            review_required=validation.review_required,
        )


__all__ = [
    "IntelligenceOrchestrationHandoff",
    "IntelligenceOrchestrationHandoffBoundary",
]
