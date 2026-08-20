"""
V10 intelligence feedback consumption boundary.

Consumes execution feedback and converts it into an immutable,
provider-independent intelligence signal.

The consumer interprets feedback only. It does not prescribe or perform
runtime actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from .execution_feedback import ExecutionFeedback, FeedbackSignal


class FeedbackSeverity(str, Enum):
    """Normalized severity exposed to intelligence consumers."""

    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class IntelligenceFeedback:
    """Immutable intelligence-layer representation of execution feedback."""

    execution_id: str
    context_id: UUID
    correlation_id: UUID
    signals: tuple[FeedbackSignal, ...]
    severity: FeedbackSeverity
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string")

        if not self.execution_id:
            raise ValueError("execution_id must not be empty")

        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.signals, tuple):
            raise TypeError("signals must be a tuple")

        seen: set[FeedbackSignal] = set()

        for signal in self.signals:
            if not isinstance(signal, FeedbackSignal):
                raise TypeError("signals must contain FeedbackSignal values")

            if signal in seen:
                raise ValueError("signals must not contain duplicates")

            seen.add(signal)

        if not isinstance(self.severity, FeedbackSeverity):
            raise TypeError("severity must be a FeedbackSeverity")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @classmethod
    def from_feedback(
        cls,
        feedback: ExecutionFeedback,
        *,
        severity: FeedbackSeverity,
    ) -> "IntelligenceFeedback":
        """Create an intelligence feedback result from execution feedback."""

        return cls(
            execution_id=feedback.execution_id,
            context_id=feedback.context_id,
            correlation_id=feedback.correlation_id,
            signals=feedback.signals,
            severity=severity,
            metadata=feedback.metadata,
        )


class FeedbackConsumer:
    """
    Deterministically consume execution feedback.

    This component performs interpretation only. It has no runtime
    dependencies and performs no execution, retry, re-planning, or
    strategy-selection operations.
    """

    _SEVERITY_RANK = {
        FeedbackSeverity.NONE: 0,
        FeedbackSeverity.INFO: 1,
        FeedbackSeverity.WARNING: 2,
        FeedbackSeverity.CRITICAL: 3,
    }

    _SIGNAL_SEVERITY = {
        FeedbackSignal.SUCCESS: FeedbackSeverity.NONE,
        FeedbackSignal.EVALUATION_UNKNOWN: FeedbackSeverity.INFO,
        FeedbackSignal.RETRY_OBSERVED: FeedbackSeverity.WARNING,
        FeedbackSignal.FALLBACK_USED: FeedbackSeverity.WARNING,
        FeedbackSignal.QUALITY_DEGRADED: FeedbackSeverity.WARNING,
        FeedbackSignal.PERFORMANCE_DEGRADED: FeedbackSeverity.WARNING,
        FeedbackSignal.RELIABILITY_DEGRADED: FeedbackSeverity.WARNING,
        FeedbackSignal.EXECUTION_PARTIAL: FeedbackSeverity.WARNING,
        FeedbackSignal.EXECUTION_FAILED: FeedbackSeverity.CRITICAL,
        FeedbackSignal.EXECUTION_CANCELLED: FeedbackSeverity.CRITICAL,
    }

    def consume(
        self,
        feedback: ExecutionFeedback,
    ) -> IntelligenceFeedback:
        """Consume execution feedback without causing runtime side effects."""

        if not isinstance(feedback, ExecutionFeedback):
            raise TypeError("feedback must be an ExecutionFeedback")

        severity = self._derive_severity(feedback.signals)

        return IntelligenceFeedback.from_feedback(
            feedback,
            severity=severity,
        )

    @classmethod
    def _derive_severity(
        cls,
        signals: tuple[FeedbackSignal, ...],
    ) -> FeedbackSeverity:
        severity = FeedbackSeverity.NONE

        for signal in signals:
            candidate = cls._SIGNAL_SEVERITY[signal]

            if cls._SEVERITY_RANK[candidate] > cls._SEVERITY_RANK[severity]:
                severity = candidate

        return severity


__all__ = [
    "FeedbackConsumer",
    "FeedbackSeverity",
    "IntelligenceFeedback",
]
