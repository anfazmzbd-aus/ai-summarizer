"""
V10 M7 orchestration directive contract.

Defines the immutable representation passed from bounded intelligence
into orchestration.

M7.1 defines representation only. It does not translate adaptation
dispositions, validate orchestration policy, or execute runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .adaptation_decision import AdaptationDisposition
from .task_decision import TaskAction


class OrchestrationDisposition(str, Enum):
    """Bounded orchestration intent."""

    NO_CHANGE = "no_change"
    ADVISORY_CONTEXT = "advisory_context"
    BOUNDED_CONSTRAINT = "bounded_constraint"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True, slots=True)
class OrchestrationDirective:
    """
    Immutable orchestration intent derived from bounded intelligence.

    This contract intentionally contains no provider, strategy, retry,
    timeout, or execution configuration.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    adaptation_disposition: AdaptationDisposition
    orchestration_disposition: OrchestrationDisposition

    execution_change_allowed: bool
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
            self.execution_change_allowed,
            bool,
        ):
            raise TypeError("execution_change_allowed must be a bool")

        if not isinstance(
            self.review_required,
            bool,
        ):
            raise TypeError("review_required must be a bool")

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID,
        correlation_id: UUID,
        action: TaskAction,
        adaptation_disposition: AdaptationDisposition,
        orchestration_disposition: OrchestrationDisposition,
        execution_change_allowed: bool,
        review_required: bool,
        reasons: tuple[str, ...],
    ) -> "OrchestrationDirective":
        """Create an immutable orchestration directive."""

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
            adaptation_disposition=adaptation_disposition,
            orchestration_disposition=orchestration_disposition,
            execution_change_allowed=execution_change_allowed,
            review_required=review_required,
            reasons=reasons,
        )


__all__ = [
    "OrchestrationDirective",
    "OrchestrationDisposition",
]
