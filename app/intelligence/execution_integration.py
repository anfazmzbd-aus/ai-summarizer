"""
V10 M7 existing execution integration adapter.

Translates a validated IntelligenceOrchestrationHandoff into an immutable,
execution-neutral integration directive.

M7.5 does not execute runtime behavior, select providers, choose strategies,
perform retries, alter timeouts, modify execution graphs, or mutate existing
execution state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

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


class ExecutionIntegrationMode(str, Enum):
    """Execution-neutral integration mode."""

    PRESERVE = "preserve"
    ADVISORY = "advisory"
    CONSTRAINED = "constrained"
    REVIEW = "review"


@dataclass(frozen=True, slots=True)
class ExecutionIntegrationDirective:
    """
    Immutable execution-facing integration guidance.

    The directive describes how existing execution behavior should be
    approached without containing provider, strategy, retry, timeout,
    or runtime configuration.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    mode: ExecutionIntegrationMode

    preserve_existing_behavior: bool
    execution_change_authorized: bool
    bounded_constraint_required: bool
    review_required: bool

    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.mode,
            ExecutionIntegrationMode,
        ):
            raise TypeError("mode must be an ExecutionIntegrationMode")

        boolean_fields = {
            "preserve_existing_behavior": (self.preserve_existing_behavior),
            "execution_change_authorized": (self.execution_change_authorized),
            "bounded_constraint_required": (self.bounded_constraint_required),
            "review_required": self.review_required,
        }

        for name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

        self._validate_mode_semantics()

    def _validate_mode_semantics(self) -> None:
        if self.mode is ExecutionIntegrationMode.PRESERVE:
            if not self.preserve_existing_behavior:
                raise ValueError("PRESERVE mode must preserve existing behavior")

            if self.execution_change_authorized:
                raise ValueError("PRESERVE mode cannot authorize execution changes")

            if self.bounded_constraint_required:
                raise ValueError("PRESERVE mode cannot require bounded constraints")

            if self.review_required:
                raise ValueError("PRESERVE mode cannot require review")

            return

        if self.mode is ExecutionIntegrationMode.ADVISORY:
            if not self.preserve_existing_behavior:
                raise ValueError("ADVISORY mode must preserve existing behavior")

            if self.execution_change_authorized:
                raise ValueError("ADVISORY mode cannot authorize execution changes")

            if self.bounded_constraint_required:
                raise ValueError("ADVISORY mode cannot require bounded constraints")

            if self.review_required:
                raise ValueError("ADVISORY mode cannot require review")

            return

        if self.mode is ExecutionIntegrationMode.CONSTRAINED:
            if not self.preserve_existing_behavior:
                raise ValueError("CONSTRAINED mode must preserve existing behavior")

            if not self.execution_change_authorized:
                raise ValueError("CONSTRAINED mode requires execution change authority")

            if not self.bounded_constraint_required:
                raise ValueError("CONSTRAINED mode requires bounded constraints")

            if self.review_required:
                raise ValueError("CONSTRAINED mode cannot require review")

            return

        if self.mode is ExecutionIntegrationMode.REVIEW:
            if not self.preserve_existing_behavior:
                raise ValueError("REVIEW mode must preserve existing behavior")

            if self.execution_change_authorized:
                raise ValueError("REVIEW mode cannot authorize execution changes")

            if self.bounded_constraint_required:
                raise ValueError("REVIEW mode cannot require bounded constraints")

            if not self.review_required:
                raise ValueError("REVIEW mode requires review")


class ExistingExecutionIntegrationAdapter:
    """
    Adapt validated intelligence orchestration handoff into execution-neutral
    integration guidance.

    The adapter does not call or mutate the existing execution runtime.
    """

    def adapt(
        self,
        handoff: IntelligenceOrchestrationHandoff,
    ) -> ExecutionIntegrationDirective:
        """Translate one validated handoff into execution integration intent."""

        if not isinstance(
            handoff,
            IntelligenceOrchestrationHandoff,
        ):
            raise TypeError("handoff must be an " "IntelligenceOrchestrationHandoff")

        self._validate_handoff(handoff)

        mode = self._derive_mode(handoff.orchestration_disposition)

        preserve_existing_behavior = True

        execution_change_authorized = mode is ExecutionIntegrationMode.CONSTRAINED

        bounded_constraint_required = mode is ExecutionIntegrationMode.CONSTRAINED

        review_required = mode is ExecutionIntegrationMode.REVIEW

        reasons = self._build_reasons(
            handoff=handoff,
            mode=mode,
        )

        return ExecutionIntegrationDirective(
            context_id=handoff.context_id,
            correlation_id=handoff.correlation_id,
            action=handoff.action,
            mode=mode,
            preserve_existing_behavior=(preserve_existing_behavior),
            execution_change_authorized=(execution_change_authorized),
            bounded_constraint_required=(bounded_constraint_required),
            review_required=review_required,
            reasons=reasons,
        )

    @staticmethod
    def _validate_handoff(
        handoff: IntelligenceOrchestrationHandoff,
    ) -> None:
        if handoff.validation.status is not DirectiveValidationStatus.VALID:
            raise ValueError("handoff requires valid directive validation")

        if handoff.validation.directive != handoff.directive:
            raise ValueError("handoff validation directive must match directive")

        if handoff.execution_authorized is not handoff.validation.execution_authorized:
            raise ValueError("handoff execution authority must match validation")

        if handoff.review_required is not handoff.validation.review_required:
            raise ValueError("handoff review requirement must match validation")

    @staticmethod
    def _derive_mode(
        disposition: OrchestrationDisposition,
    ) -> ExecutionIntegrationMode:
        if disposition is OrchestrationDisposition.NO_CHANGE:
            return ExecutionIntegrationMode.PRESERVE

        if disposition is OrchestrationDisposition.ADVISORY_CONTEXT:
            return ExecutionIntegrationMode.ADVISORY

        if disposition is OrchestrationDisposition.BOUNDED_CONSTRAINT:
            return ExecutionIntegrationMode.CONSTRAINED

        if disposition is OrchestrationDisposition.REVIEW_REQUIRED:
            return ExecutionIntegrationMode.REVIEW

        raise ValueError("unsupported orchestration disposition")

    @staticmethod
    def _build_reasons(
        *,
        handoff: IntelligenceOrchestrationHandoff,
        mode: ExecutionIntegrationMode,
    ) -> tuple[str, ...]:
        reasons: list[str] = list(handoff.validation.reasons)

        if mode is ExecutionIntegrationMode.PRESERVE:
            reasons.append("existing execution behavior remains unchanged")

        elif mode is ExecutionIntegrationMode.ADVISORY:
            reasons.append(
                "existing execution behavior remains unchanged "
                "while advisory intelligence context is preserved"
            )

        elif mode is ExecutionIntegrationMode.CONSTRAINED:
            reasons.append(
                "existing execution behavior is preserved while "
                "approved bounded constraints are required"
            )

        else:
            reasons.append(
                "existing execution behavior is preserved pending "
                "review-oriented handling"
            )

        return tuple(reasons)


__all__ = [
    "ExecutionIntegrationDirective",
    "ExecutionIntegrationMode",
    "ExistingExecutionIntegrationAdapter",
]
