"""
V10 M8 intelligence observability event / diagnostic boundary.

Defines a deterministic, immutable diagnostic representation derived from
IntelligenceObservabilitySummary.

M8.5 produces data only. It does not emit logs, publish telemetry, call
metrics systems, invoke runtime behavior, or alter intelligence decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .observability_summary import (
    IntelligenceObservabilityStatus,
    IntelligenceObservabilitySummary,
)
from .task_decision import TaskAction


class IntelligenceObservabilitySeverity(str, Enum):
    """Operational severity for intelligence diagnostic events."""

    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    REVIEW = "review"


@dataclass(frozen=True, slots=True)
class IntelligenceObservabilityEvent:
    """
    Immutable diagnostic event for one intelligence lifecycle summary.

    The event is suitable for later logging, telemetry, API diagnostics,
    or frontend inspection without coupling M8 to those systems.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    status: IntelligenceObservabilityStatus
    severity: IntelligenceObservabilitySeverity

    historical_influence_applied: bool
    adaptation_applied: bool
    execution_authorized: bool
    review_required: bool

    reason_count: int

    diagnostic_code: str
    message: str

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
            self.severity,
            IntelligenceObservabilitySeverity,
        ):
            raise TypeError("severity must be an IntelligenceObservabilitySeverity")

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

        if not isinstance(
            self.diagnostic_code,
            str,
        ):
            raise TypeError("diagnostic_code must be a string")

        if not self.diagnostic_code:
            raise ValueError("diagnostic_code must not be empty")

        if not isinstance(
            self.message,
            str,
        ):
            raise TypeError("message must be a string")

        if not self.message:
            raise ValueError("message must not be empty")


class ObservabilityEventBuilder:
    """Build deterministic diagnostic events from observability summaries."""

    def build(
        self,
        summary: IntelligenceObservabilitySummary,
    ) -> IntelligenceObservabilityEvent:
        """Build one immutable intelligence diagnostic event."""

        if not isinstance(
            summary,
            IntelligenceObservabilitySummary,
        ):
            raise TypeError("summary must be an " "IntelligenceObservabilitySummary")

        severity = self._derive_severity(summary.status)

        diagnostic_code = self._derive_diagnostic_code(summary.status)

        message = self._derive_message(summary.status)

        return IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=severity,
            historical_influence_applied=(summary.historical_influence_applied),
            adaptation_applied=summary.adaptation_applied,
            execution_authorized=summary.execution_authorized,
            review_required=summary.review_required,
            reason_count=summary.reason_count,
            diagnostic_code=diagnostic_code,
            message=message,
        )

    @staticmethod
    def _derive_severity(
        status: IntelligenceObservabilityStatus,
    ) -> IntelligenceObservabilitySeverity:
        if status is IntelligenceObservabilityStatus.NORMAL:
            return IntelligenceObservabilitySeverity.INFO

        if status is IntelligenceObservabilityStatus.ADVISORY:
            return IntelligenceObservabilitySeverity.NOTICE

        if status is IntelligenceObservabilityStatus.CONSTRAINED:
            return IntelligenceObservabilitySeverity.WARNING

        if status is IntelligenceObservabilityStatus.REVIEW_REQUIRED:
            return IntelligenceObservabilitySeverity.REVIEW

        raise ValueError("unsupported intelligence observability status")

    @staticmethod
    def _derive_diagnostic_code(
        status: IntelligenceObservabilityStatus,
    ) -> str:
        if status is IntelligenceObservabilityStatus.NORMAL:
            return "INTELLIGENCE_NORMAL"

        if status is IntelligenceObservabilityStatus.ADVISORY:
            return "INTELLIGENCE_ADVISORY"

        if status is IntelligenceObservabilityStatus.CONSTRAINED:
            return "INTELLIGENCE_CONSTRAINED"

        if status is IntelligenceObservabilityStatus.REVIEW_REQUIRED:
            return "INTELLIGENCE_REVIEW_REQUIRED"

        raise ValueError("unsupported intelligence observability status")

    @staticmethod
    def _derive_message(
        status: IntelligenceObservabilityStatus,
    ) -> str:
        if status is IntelligenceObservabilityStatus.NORMAL:
            return (
                "intelligence lifecycle completed with normal "
                "execution-preserving behavior"
            )

        if status is IntelligenceObservabilityStatus.ADVISORY:
            return "intelligence lifecycle includes advisory " "historical context"

        if status is IntelligenceObservabilityStatus.CONSTRAINED:
            return (
                "intelligence lifecycle requires approved "
                "bounded execution constraints"
            )

        if status is IntelligenceObservabilityStatus.REVIEW_REQUIRED:
            return "intelligence lifecycle requires review-oriented " "handling"

        raise ValueError("unsupported intelligence observability status")


__all__ = [
    "IntelligenceObservabilityEvent",
    "IntelligenceObservabilitySeverity",
    "ObservabilityEventBuilder",
]
