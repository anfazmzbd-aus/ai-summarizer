"""
V10 execution feedback contracts.

Converts execution observations and evaluation results into deterministic,
provider-independent feedback signals for the intelligence layer.

Feedback describes what intelligence should know. It does not prescribe
runtime actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .evaluation_result import EvaluationResult, EvaluationStatus
from .execution_observation import ExecutionObservation, ExecutionOutcome


class FeedbackSignal(str, Enum):
    """Normalized execution signals exposed to the intelligence layer."""

    SUCCESS = "success"
    QUALITY_DEGRADED = "quality_degraded"
    PERFORMANCE_DEGRADED = "performance_degraded"
    RELIABILITY_DEGRADED = "reliability_degraded"
    FALLBACK_USED = "fallback_used"
    RETRY_OBSERVED = "retry_observed"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_PARTIAL = "execution_partial"
    EXECUTION_CANCELLED = "execution_cancelled"
    EVALUATION_UNKNOWN = "evaluation_unknown"


@dataclass(frozen=True, slots=True)
class ExecutionFeedback:
    """Immutable feedback derived from one execution and its evaluation."""

    execution_id: str
    context_id: Any
    correlation_id: Any

    evaluation_status: EvaluationStatus

    signals: tuple[FeedbackSignal, ...] = ()

    reasons: tuple[str, ...] = ()

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string")

        if not self.execution_id:
            raise ValueError("execution_id must not be empty")

        if not isinstance(self.evaluation_status, EvaluationStatus):
            raise TypeError("evaluation_status must be an EvaluationStatus")

        if not isinstance(self.signals, tuple):
            raise TypeError("signals must be a tuple")

        seen: set[FeedbackSignal] = set()

        for signal in self.signals:
            if not isinstance(signal, FeedbackSignal):
                raise TypeError("feedback signals must be FeedbackSignal values")

            if signal in seen:
                raise ValueError("feedback signals must not contain duplicates")

            seen.add(signal)

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("feedback reasons must be strings")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @classmethod
    def create(
        cls,
        *,
        execution_id: str,
        context_id: Any,
        correlation_id: Any,
        evaluation_status: EvaluationStatus,
        signals: tuple[FeedbackSignal, ...] = (),
        reasons: tuple[str, ...] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> "ExecutionFeedback":
        """Create an immutable execution feedback object."""

        return cls(
            execution_id=execution_id,
            context_id=context_id,
            correlation_id=correlation_id,
            evaluation_status=evaluation_status,
            signals=signals,
            reasons=reasons,
            metadata={} if metadata is None else metadata,
        )


class ExecutionFeedbackBuilder:
    """Build deterministic feedback from observation and evaluation."""

    _SIGNAL_ORDER = {
        FeedbackSignal.SUCCESS: 0,
        FeedbackSignal.EXECUTION_FAILED: 1,
        FeedbackSignal.EXECUTION_PARTIAL: 2,
        FeedbackSignal.EXECUTION_CANCELLED: 3,
        FeedbackSignal.QUALITY_DEGRADED: 4,
        FeedbackSignal.PERFORMANCE_DEGRADED: 5,
        FeedbackSignal.RELIABILITY_DEGRADED: 6,
        FeedbackSignal.RETRY_OBSERVED: 7,
        FeedbackSignal.FALLBACK_USED: 8,
        FeedbackSignal.EVALUATION_UNKNOWN: 9,
    }

    def build(
        self,
        observation: ExecutionObservation,
        evaluation: EvaluationResult,
    ) -> ExecutionFeedback:
        """Build feedback from a matching observation and evaluation."""

        self._validate_inputs(observation, evaluation)

        signals: set[FeedbackSignal] = set()

        self._add_outcome_signal(
            observation.outcome,
            signals,
        )

        self._add_evaluation_signals(
            evaluation,
            signals,
        )

        if observation.retry_count > 0:
            signals.add(FeedbackSignal.RETRY_OBSERVED)

        if observation.fallback_used:
            signals.add(FeedbackSignal.FALLBACK_USED)

        ordered_signals = tuple(
            sorted(
                signals,
                key=self._SIGNAL_ORDER.__getitem__,
            )
        )

        return ExecutionFeedback.create(
            execution_id=observation.execution_id,
            context_id=observation.context_id,
            correlation_id=observation.correlation_id,
            evaluation_status=evaluation.status,
            signals=ordered_signals,
            reasons=evaluation.reasons,
        )

    @staticmethod
    def _validate_inputs(
        observation: ExecutionObservation,
        evaluation: EvaluationResult,
    ) -> None:
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")

        if not isinstance(evaluation, EvaluationResult):
            raise TypeError("evaluation must be an EvaluationResult")

        if observation.execution_id != evaluation.execution_id:
            raise ValueError("observation and evaluation execution_id must match")

        if observation.context_id != evaluation.context_id:
            raise ValueError("observation and evaluation context_id must match")

        if observation.correlation_id != evaluation.correlation_id:
            raise ValueError("observation and evaluation correlation_id must match")

    @staticmethod
    def _add_outcome_signal(
        outcome: ExecutionOutcome,
        signals: set[FeedbackSignal],
    ) -> None:
        if outcome is ExecutionOutcome.SUCCESS:
            signals.add(FeedbackSignal.SUCCESS)
        elif outcome is ExecutionOutcome.FAILED:
            signals.add(FeedbackSignal.EXECUTION_FAILED)
        elif outcome is ExecutionOutcome.PARTIAL:
            signals.add(FeedbackSignal.EXECUTION_PARTIAL)
        elif outcome is ExecutionOutcome.CANCELLED:
            signals.add(FeedbackSignal.EXECUTION_CANCELLED)

    @staticmethod
    def _add_evaluation_signals(
        evaluation: EvaluationResult,
        signals: set[FeedbackSignal],
    ) -> None:
        if evaluation.status is EvaluationStatus.UNKNOWN:
            signals.add(FeedbackSignal.EVALUATION_UNKNOWN)

        if evaluation.dimensions.get("quality") is EvaluationStatus.DEGRADED:
            signals.add(FeedbackSignal.QUALITY_DEGRADED)

        if evaluation.dimensions.get("performance") is EvaluationStatus.DEGRADED:
            signals.add(FeedbackSignal.PERFORMANCE_DEGRADED)

        if evaluation.dimensions.get("reliability") is EvaluationStatus.DEGRADED:
            signals.add(FeedbackSignal.RELIABILITY_DEGRADED)


__all__ = [
    "ExecutionFeedback",
    "ExecutionFeedbackBuilder",
    "FeedbackSignal",
]
