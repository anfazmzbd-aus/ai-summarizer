"""
V10 M8 explainability integration and safety boundary.

Composes the intelligence trace, observability summary, and diagnostic
event into one immutable, provenance-safe snapshot.

M8.6 performs validation and composition only. It does not emit telemetry,
modify intelligence behavior, invoke runtime components, or create
execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .intelligence_trace import IntelligenceTrace
from .observability_event import (
    IntelligenceObservabilityEvent,
    IntelligenceObservabilitySeverity,
)
from .observability_summary import (
    IntelligenceObservabilityStatus,
    IntelligenceObservabilitySummary,
)
from .task_decision import TaskAction


@dataclass(frozen=True, slots=True)
class IntelligenceObservabilitySnapshot:
    """
    Immutable integrated observability representation.

    This is the final M8 intelligence observability handoff suitable for
    later infrastructure adapters, diagnostics APIs, or product surfaces.
    """

    context_id: UUID
    correlation_id: UUID
    action: TaskAction

    trace: IntelligenceTrace
    summary: IntelligenceObservabilitySummary
    event: IntelligenceObservabilityEvent

    status: IntelligenceObservabilityStatus
    severity: IntelligenceObservabilitySeverity

    historical_influence_applied: bool
    adaptation_applied: bool
    execution_authorized: bool
    review_required: bool

    reason_count: int
    diagnostic_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(self.trace, IntelligenceTrace):
            raise TypeError("trace must be an IntelligenceTrace")

        if not isinstance(
            self.summary,
            IntelligenceObservabilitySummary,
        ):
            raise TypeError("summary must be an " "IntelligenceObservabilitySummary")

        if not isinstance(
            self.event,
            IntelligenceObservabilityEvent,
        ):
            raise TypeError("event must be an IntelligenceObservabilityEvent")

        if not isinstance(
            self.status,
            IntelligenceObservabilityStatus,
        ):
            raise TypeError("status must be an " "IntelligenceObservabilityStatus")

        if not isinstance(
            self.severity,
            IntelligenceObservabilitySeverity,
        ):
            raise TypeError("severity must be an " "IntelligenceObservabilitySeverity")

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

        self._validate_consistency()

    def _validate_consistency(self) -> None:
        if self.context_id != self.trace.context_id:
            raise ValueError("context_id must match trace")

        if self.correlation_id != self.trace.correlation_id:
            raise ValueError("correlation_id must match trace")

        if self.action is not self.trace.action:
            raise ValueError("action must match trace")

        if self.summary.context_id != self.context_id:
            raise ValueError("summary context_id must match snapshot")

        if self.summary.correlation_id != self.correlation_id:
            raise ValueError("summary correlation_id must match snapshot")

        if self.summary.action is not self.action:
            raise ValueError("summary action must match snapshot")

        if self.event.context_id != self.context_id:
            raise ValueError("event context_id must match snapshot")

        if self.event.correlation_id != self.correlation_id:
            raise ValueError("event correlation_id must match snapshot")

        if self.event.action is not self.action:
            raise ValueError("event action must match snapshot")

        if self.status is not self.summary.status:
            raise ValueError("status must match summary")

        if self.event.status is not self.status:
            raise ValueError("event status must match snapshot")

        if self.severity is not self.event.severity:
            raise ValueError("severity must match event")

        if (
            self.historical_influence_applied
            is not self.trace.historical_influence_applied
        ):
            raise ValueError("historical_influence_applied must match trace")

        if (
            self.summary.historical_influence_applied
            is not self.historical_influence_applied
        ):
            raise ValueError("summary historical influence must match snapshot")

        if (
            self.event.historical_influence_applied
            is not self.historical_influence_applied
        ):
            raise ValueError("event historical influence must match snapshot")

        if self.adaptation_applied is not self.trace.adaptation_applied:
            raise ValueError("adaptation_applied must match trace")

        if self.summary.adaptation_applied is not self.adaptation_applied:
            raise ValueError("summary adaptation state must match snapshot")

        if self.event.adaptation_applied is not self.adaptation_applied:
            raise ValueError("event adaptation state must match snapshot")

        if self.execution_authorized is not self.trace.execution_authorized:
            raise ValueError("execution_authorized must match trace")

        if self.summary.execution_authorized is not self.execution_authorized:
            raise ValueError("summary execution authority must match snapshot")

        if self.event.execution_authorized is not self.execution_authorized:
            raise ValueError("event execution authority must match snapshot")

        if self.review_required is not self.trace.review_required:
            raise ValueError("review_required must match trace")

        if self.summary.review_required is not self.review_required:
            raise ValueError("summary review requirement must match snapshot")

        if self.event.review_required is not self.review_required:
            raise ValueError("event review requirement must match snapshot")

        if self.reason_count != self.summary.reason_count:
            raise ValueError("reason_count must match summary")

        if self.event.reason_count != self.reason_count:
            raise ValueError("event reason_count must match snapshot")

        if self.diagnostic_code != self.event.diagnostic_code:
            raise ValueError("diagnostic_code must match event")


class IntelligenceObservabilityIntegrationBoundary:
    """Compose the complete validated M8 observability chain."""

    def compose(
        self,
        trace: IntelligenceTrace,
        summary: IntelligenceObservabilitySummary,
        event: IntelligenceObservabilityEvent,
    ) -> IntelligenceObservabilitySnapshot:
        """Compose one validated observability snapshot."""

        if not isinstance(trace, IntelligenceTrace):
            raise TypeError("trace must be an IntelligenceTrace")

        if not isinstance(
            summary,
            IntelligenceObservabilitySummary,
        ):
            raise TypeError("summary must be an " "IntelligenceObservabilitySummary")

        if not isinstance(
            event,
            IntelligenceObservabilityEvent,
        ):
            raise TypeError("event must be an IntelligenceObservabilityEvent")

        return IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=summary.reason_count,
            diagnostic_code=event.diagnostic_code,
        )


__all__ = [
    "IntelligenceObservabilityIntegrationBoundary",
    "IntelligenceObservabilitySnapshot",
]
