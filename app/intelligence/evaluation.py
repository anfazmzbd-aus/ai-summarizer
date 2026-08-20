"""
V10 deterministic execution evaluation boundary.

Evaluates ExecutionObservation against explicit execution criteria.

This module deliberately does not perform provider calls or domain-specific
quality evaluation.
"""

from __future__ import annotations
from collections.abc import Iterable

from dataclasses import dataclass

# from typing import Mapping

from .evaluation_result import EvaluationResult, EvaluationStatus
from .execution_observation import ExecutionObservation, ExecutionOutcome


@dataclass(frozen=True, slots=True)
class EvaluationCriteria:
    """Explicit deterministic criteria for evaluating an execution."""

    require_success: bool = True
    max_duration_ms: float | None = None
    max_retries: int | None = None
    allow_fallback: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.require_success, bool):
            raise TypeError("require_success must be a bool")

        if self.max_duration_ms is not None:
            if not isinstance(
                self.max_duration_ms,
                (int, float),
            ) or isinstance(self.max_duration_ms, bool):
                raise TypeError("max_duration_ms must be a number or None")

            if self.max_duration_ms < 0:
                raise ValueError("max_duration_ms must be greater than or equal to 0")

        if self.max_retries is not None:
            if not isinstance(self.max_retries, int) or isinstance(
                self.max_retries,
                bool,
            ):
                raise TypeError("max_retries must be an integer or None")

            if self.max_retries < 0:
                raise ValueError("max_retries must be greater than or equal to 0")

        if not isinstance(self.allow_fallback, bool):
            raise TypeError("allow_fallback must be a bool")


class ExecutionEvaluator:
    """Deterministically evaluate an execution observation."""

    def evaluate(
        self,
        observation: ExecutionObservation,
        criteria: EvaluationCriteria,
    ) -> EvaluationResult:
        """Evaluate an execution observation against explicit criteria."""

        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")

        if not isinstance(criteria, EvaluationCriteria):
            raise TypeError("criteria must be an EvaluationCriteria")

        dimensions: dict[str, EvaluationStatus] = {}
        reasons: list[str] = []

        self._evaluate_outcome(
            observation,
            criteria,
            dimensions,
            reasons,
        )

        self._evaluate_performance(
            observation,
            criteria,
            dimensions,
            reasons,
        )

        self._evaluate_reliability(
            observation,
            criteria,
            dimensions,
            reasons,
        )

        status = self._derive_overall_status(
            dimensions.values(),
        )

        return EvaluationResult.create(
            execution_id=observation.execution_id,
            context_id=observation.context_id,
            correlation_id=observation.correlation_id,
            status=status,
            dimensions=dimensions,
            reasons=tuple(reasons),
        )

    @staticmethod
    def _evaluate_outcome(
        observation: ExecutionObservation,
        criteria: EvaluationCriteria,
        dimensions: dict[str, EvaluationStatus],
        reasons: list[str],
    ) -> None:
        if observation.outcome is ExecutionOutcome.SUCCESS:
            dimensions["outcome"] = EvaluationStatus.PASS
            return

        if observation.outcome is ExecutionOutcome.FAILED:
            if criteria.require_success:
                dimensions["outcome"] = EvaluationStatus.FAIL
                reasons.append("execution failed")
            else:
                dimensions["outcome"] = EvaluationStatus.DEGRADED
                reasons.append("execution failed but success was not required")
            return

        if observation.outcome is ExecutionOutcome.CANCELLED:
            dimensions["outcome"] = EvaluationStatus.FAIL
            reasons.append("execution was cancelled")
            return

        if observation.outcome is ExecutionOutcome.PARTIAL:
            dimensions["outcome"] = EvaluationStatus.DEGRADED
            reasons.append("execution completed partially")
            return

        dimensions["outcome"] = EvaluationStatus.UNKNOWN
        reasons.append("execution outcome could not be evaluated")

    @staticmethod
    def _evaluate_performance(
        observation: ExecutionObservation,
        criteria: EvaluationCriteria,
        dimensions: dict[str, EvaluationStatus],
        reasons: list[str],
    ) -> None:
        if criteria.max_duration_ms is None:
            dimensions["performance"] = EvaluationStatus.UNKNOWN
            return

        if observation.duration_ms <= criteria.max_duration_ms:
            dimensions["performance"] = EvaluationStatus.PASS
            return

        dimensions["performance"] = EvaluationStatus.DEGRADED

        reasons.append("execution duration exceeded the configured maximum")

    @staticmethod
    def _evaluate_reliability(
        observation: ExecutionObservation,
        criteria: EvaluationCriteria,
        dimensions: dict[str, EvaluationStatus],
        reasons: list[str],
    ) -> None:
        violations: list[str] = []

        if (
            criteria.max_retries is not None
            and observation.retry_count > criteria.max_retries
        ):
            violations.append("retry count exceeded the configured maximum")

        if observation.fallback_used and not criteria.allow_fallback:
            violations.append("fallback execution was not allowed")

        if violations:
            dimensions["reliability"] = EvaluationStatus.DEGRADED
            reasons.extend(violations)
            return

        if criteria.max_retries is None and criteria.allow_fallback:
            dimensions["reliability"] = EvaluationStatus.UNKNOWN
            return

        dimensions["reliability"] = EvaluationStatus.PASS

    @staticmethod
    def _derive_overall_status(
        statuses: Iterable[EvaluationStatus],
    ) -> EvaluationStatus:
        values = list(statuses)

        if not values:
            return EvaluationStatus.UNKNOWN

        if EvaluationStatus.FAIL in values:
            return EvaluationStatus.FAIL

        if EvaluationStatus.DEGRADED in values:
            return EvaluationStatus.DEGRADED

        if all(status is EvaluationStatus.PASS for status in values):
            return EvaluationStatus.PASS

        return EvaluationStatus.UNKNOWN


__all__ = ["ExecutionEvaluator", "EvaluationCriteria"]
