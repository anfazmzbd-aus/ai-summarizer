"""
V10 M8 intelligence observability summary contract.

Defines the immutable compact operational representation of an
IntelligenceTrace.

M8.3 defines representation only. It does not derive observability state,
generate diagnostics, calculate scores, or modify intelligence behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .adaptation_decision import AdaptationDisposition
from .execution_integration import ExecutionIntegrationMode
from .orchestration_directive import OrchestrationDisposition
from .task_decision import TaskAction


class IntelligenceObservabilityStatus(str, Enum):
    """Compact system-level intelligence observability state."""

    NORMAL = "normal"
    ADVISORY = "advisory"
    CONSTRAINED = "constrained"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True, slots=True)
class IntelligenceObservabilitySummary:
    """
    Immutable operational summary of one intelligence lifecycle trace.

    The summary exposes existing intelligence state without introducing
    decision authority, runtime configuration, scoring, or prediction.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    status: IntelligenceObservabilityStatus

    adaptation_disposition: AdaptationDisposition
    orchestration_disposition: OrchestrationDisposition
    integration_mode: ExecutionIntegrationMode

    historical_influence_applied: bool
    adaptation_applied: bool
    execution_authorized: bool
    review_required: bool

    reason_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(
            self.status,
            IntelligenceObservabilityStatus,
        ):
            raise TypeError("status must be an IntelligenceObservabilityStatus")

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
            self.integration_mode,
            ExecutionIntegrationMode,
        ):
            raise TypeError("integration_mode must be an " "ExecutionIntegrationMode")

        boolean_fields = {
            "historical_influence_applied": (self.historical_influence_applied),
            "adaptation_applied": self.adaptation_applied,
            "execution_authorized": self.execution_authorized,
            "review_required": self.review_required,
        }

        for name, value in boolean_fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be a bool")

        if not isinstance(
            self.reason_count,
            int,
        ) or isinstance(
            self.reason_count,
            bool,
        ):
            raise TypeError("reason_count must be an integer")

        if self.reason_count < 0:
            raise ValueError("reason_count must be greater than or equal to 0")


__all__ = [
    "IntelligenceObservabilityStatus",
    "IntelligenceObservabilitySummary",
]
