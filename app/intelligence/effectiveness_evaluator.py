"""
V10 deterministic decision effectiveness evaluation boundary.

Evaluates a TaskDecision against normalized ExecutionFeedback and produces
a DecisionEffectiveness result.

The evaluator performs interpretation only. It does not execute, retry,
replan, switch providers, select strategies, mutate runtime state, or
perform adaptive learning.
"""

from __future__ import annotations

from .decision_effectiveness import (
    DecisionEffectiveness,
    EffectivenessDimension,
    EffectivenessStatus,
)
from .execution_feedback import ExecutionFeedback, FeedbackSignal
from .task_decision import TaskDecision


class DecisionEffectivenessEvaluator:
    """Deterministically evaluate a decision using execution feedback."""

    def evaluate(
        self,
        decision: TaskDecision,
        feedback: ExecutionFeedback,
    ) -> DecisionEffectiveness:
        """
        Evaluate the effectiveness of a decision.

        The decision and feedback must belong to the same intelligence
        context and correlation chain.
        """

        self._validate_inputs(decision, feedback)

        signals = frozenset(feedback.signals)

        dimensions = {
            EffectivenessDimension.OUTCOME: self._evaluate_outcome(signals),
            EffectivenessDimension.QUALITY: self._evaluate_quality(signals),
            EffectivenessDimension.PERFORMANCE: self._evaluate_performance(signals),
            EffectivenessDimension.RELIABILITY: self._evaluate_reliability(signals),
        }

        status = self._derive_overall_status(
            signals=signals,
            dimensions=dimensions,
        )

        reasons = self._build_reasons(signals)

        return DecisionEffectiveness.create(
            context_id=decision.context_id,
            correlation_id=decision.correlation_id,
            execution_id=feedback.execution_id,
            status=status,
            dimensions=dimensions,
            reasons=reasons,
        )

    @staticmethod
    def _validate_inputs(
        decision: TaskDecision,
        feedback: ExecutionFeedback,
    ) -> None:
        if not isinstance(decision, TaskDecision):
            raise TypeError("decision must be a TaskDecision")

        if not isinstance(feedback, ExecutionFeedback):
            raise TypeError("feedback must be an ExecutionFeedback")

        if decision.context_id != feedback.context_id:
            raise ValueError("decision and feedback context_id must match")

        if decision.correlation_id != feedback.correlation_id:
            raise ValueError("decision and feedback correlation_id must match")

    @staticmethod
    def _evaluate_outcome(
        signals: frozenset[FeedbackSignal],
    ) -> EffectivenessStatus:
        if (
            FeedbackSignal.EXECUTION_FAILED in signals
            or FeedbackSignal.EXECUTION_CANCELLED in signals
        ):
            return EffectivenessStatus.INEFFECTIVE

        if FeedbackSignal.EXECUTION_PARTIAL in signals:
            return EffectivenessStatus.DEGRADED

        if FeedbackSignal.SUCCESS in signals:
            return EffectivenessStatus.EFFECTIVE

        return EffectivenessStatus.UNKNOWN

    @staticmethod
    def _evaluate_quality(
        signals: frozenset[FeedbackSignal],
    ) -> EffectivenessStatus:
        if FeedbackSignal.QUALITY_DEGRADED in signals:
            return EffectivenessStatus.DEGRADED

        return EffectivenessStatus.UNKNOWN

    @staticmethod
    def _evaluate_performance(
        signals: frozenset[FeedbackSignal],
    ) -> EffectivenessStatus:
        if FeedbackSignal.PERFORMANCE_DEGRADED in signals:
            return EffectivenessStatus.DEGRADED

        return EffectivenessStatus.UNKNOWN

    @staticmethod
    def _evaluate_reliability(
        signals: frozenset[FeedbackSignal],
    ) -> EffectivenessStatus:
        degradation_signals = {
            FeedbackSignal.RELIABILITY_DEGRADED,
            FeedbackSignal.RETRY_OBSERVED,
            FeedbackSignal.FALLBACK_USED,
            FeedbackSignal.EXECUTION_PARTIAL,
        }

        if signals & degradation_signals:
            return EffectivenessStatus.DEGRADED

        if (
            FeedbackSignal.EXECUTION_FAILED in signals
            or FeedbackSignal.EXECUTION_CANCELLED in signals
        ):
            return EffectivenessStatus.INEFFECTIVE

        if FeedbackSignal.SUCCESS in signals:
            return EffectivenessStatus.EFFECTIVE

        return EffectivenessStatus.UNKNOWN

    @staticmethod
    def _derive_overall_status(
        *,
        signals: frozenset[FeedbackSignal],
        dimensions: dict[
            EffectivenessDimension,
            EffectivenessStatus,
        ],
    ) -> EffectivenessStatus:
        if (
            FeedbackSignal.EXECUTION_FAILED in signals
            or FeedbackSignal.EXECUTION_CANCELLED in signals
        ):
            return EffectivenessStatus.INEFFECTIVE

        if EffectivenessStatus.DEGRADED in dimensions.values():
            return EffectivenessStatus.DEGRADED

        if FeedbackSignal.EVALUATION_UNKNOWN in signals:
            return EffectivenessStatus.UNKNOWN

        if FeedbackSignal.SUCCESS in signals:
            return EffectivenessStatus.EFFECTIVE

        return EffectivenessStatus.UNKNOWN

    @staticmethod
    def _build_reasons(
        signals: frozenset[FeedbackSignal],
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        ordered_reasons = (
            (
                FeedbackSignal.EXECUTION_FAILED,
                "execution failed",
            ),
            (
                FeedbackSignal.EXECUTION_CANCELLED,
                "execution was cancelled",
            ),
            (
                FeedbackSignal.EXECUTION_PARTIAL,
                "execution completed only partially",
            ),
            (
                FeedbackSignal.QUALITY_DEGRADED,
                "execution quality was degraded",
            ),
            (
                FeedbackSignal.PERFORMANCE_DEGRADED,
                "execution performance was degraded",
            ),
            (
                FeedbackSignal.RELIABILITY_DEGRADED,
                "execution reliability was degraded",
            ),
            (
                FeedbackSignal.RETRY_OBSERVED,
                "execution required retries",
            ),
            (
                FeedbackSignal.FALLBACK_USED,
                "execution required fallback behavior",
            ),
            (
                FeedbackSignal.EVALUATION_UNKNOWN,
                "execution evaluation was incomplete",
            ),
            (
                FeedbackSignal.SUCCESS,
                "execution succeeded",
            ),
        )

        for signal, reason in ordered_reasons:
            if signal in signals:
                reasons.append(reason)

        return tuple(reasons)


__all__ = ["DecisionEffectivenessEvaluator"]
