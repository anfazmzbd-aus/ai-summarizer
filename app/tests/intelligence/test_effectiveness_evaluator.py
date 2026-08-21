"""Tests for the V10 decision effectiveness evaluation boundary."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionEffectiveness,
    DecisionEffectivenessEvaluator,
    EffectivenessDimension,
    EffectivenessStatus,
    EvaluationStatus,
    ExecutionFeedback,
    FeedbackSignal,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    context_id=None,
    correlation_id=None,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=TaskAction.SUMMARIZE,
        reason="test decision",
        confidence=1.0,
    )


def make_feedback(
    decision: TaskDecision,
    *,
    signals: tuple[FeedbackSignal, ...],
    evaluation_status: EvaluationStatus = EvaluationStatus.PASS,
) -> ExecutionFeedback:
    return ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        evaluation_status=evaluation_status,
        signals=signals,
    )


def evaluate(
    signals: tuple[FeedbackSignal, ...],
) -> DecisionEffectiveness:
    decision = make_decision()
    feedback = make_feedback(
        decision,
        signals=signals,
    )

    return DecisionEffectivenessEvaluator().evaluate(
        decision,
        feedback,
    )


def test_evaluator_returns_decision_effectiveness() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert isinstance(result, DecisionEffectiveness)


def test_success_is_effective() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert result.status is EffectivenessStatus.EFFECTIVE


def test_success_outcome_is_effective() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.EFFECTIVE
    )


def test_success_reliability_is_effective() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert (
        result.dimensions[EffectivenessDimension.RELIABILITY]
        is EffectivenessStatus.EFFECTIVE
    )


def test_quality_is_unknown_without_quality_signal() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert (
        result.dimensions[EffectivenessDimension.QUALITY] is EffectivenessStatus.UNKNOWN
    )


def test_performance_is_unknown_without_performance_signal() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert (
        result.dimensions[EffectivenessDimension.PERFORMANCE]
        is EffectivenessStatus.UNKNOWN
    )


def test_failed_execution_is_ineffective() -> None:
    result = evaluate((FeedbackSignal.EXECUTION_FAILED,))

    assert result.status is EffectivenessStatus.INEFFECTIVE
    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.INEFFECTIVE
    )


def test_cancelled_execution_is_ineffective() -> None:
    result = evaluate((FeedbackSignal.EXECUTION_CANCELLED,))

    assert result.status is EffectivenessStatus.INEFFECTIVE
    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.INEFFECTIVE
    )


def test_partial_execution_is_degraded() -> None:
    result = evaluate((FeedbackSignal.EXECUTION_PARTIAL,))

    assert result.status is EffectivenessStatus.DEGRADED
    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.DEGRADED
    )
    assert (
        result.dimensions[EffectivenessDimension.RELIABILITY]
        is EffectivenessStatus.DEGRADED
    )


def test_quality_degradation_is_detected() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.QUALITY_DEGRADED,
        )
    )

    assert result.status is EffectivenessStatus.DEGRADED
    assert (
        result.dimensions[EffectivenessDimension.QUALITY]
        is EffectivenessStatus.DEGRADED
    )


def test_performance_degradation_is_detected() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.PERFORMANCE_DEGRADED,
        )
    )

    assert result.status is EffectivenessStatus.DEGRADED
    assert (
        result.dimensions[EffectivenessDimension.PERFORMANCE]
        is EffectivenessStatus.DEGRADED
    )


def test_reliability_degradation_is_detected() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RELIABILITY_DEGRADED,
        )
    )

    assert result.status is EffectivenessStatus.DEGRADED
    assert (
        result.dimensions[EffectivenessDimension.RELIABILITY]
        is EffectivenessStatus.DEGRADED
    )


def test_retry_degrades_reliability() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        )
    )

    assert result.status is EffectivenessStatus.DEGRADED
    assert (
        result.dimensions[EffectivenessDimension.RELIABILITY]
        is EffectivenessStatus.DEGRADED
    )


def test_fallback_degrades_reliability() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.FALLBACK_USED,
        )
    )

    assert result.status is EffectivenessStatus.DEGRADED
    assert (
        result.dimensions[EffectivenessDimension.RELIABILITY]
        is EffectivenessStatus.DEGRADED
    )


def test_unknown_evaluation_produces_unknown_overall() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.EVALUATION_UNKNOWN,
        )
    )

    assert result.status is EffectivenessStatus.UNKNOWN


def test_unknown_evaluation_does_not_erase_known_success_outcome() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.EVALUATION_UNKNOWN,
        )
    )

    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.EFFECTIVE
    )


def test_failure_has_precedence_over_unknown() -> None:
    result = evaluate(
        (
            FeedbackSignal.EXECUTION_FAILED,
            FeedbackSignal.EVALUATION_UNKNOWN,
        )
    )

    assert result.status is EffectivenessStatus.INEFFECTIVE


def test_failure_has_precedence_over_degradation() -> None:
    result = evaluate(
        (
            FeedbackSignal.EXECUTION_FAILED,
            FeedbackSignal.PERFORMANCE_DEGRADED,
        )
    )

    assert result.status is EffectivenessStatus.INEFFECTIVE


def test_degradation_has_precedence_over_unknown() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.PERFORMANCE_DEGRADED,
            FeedbackSignal.EVALUATION_UNKNOWN,
        )
    )

    assert result.status is EffectivenessStatus.DEGRADED


def test_no_signals_produces_unknown() -> None:
    result = evaluate(())

    assert result.status is EffectivenessStatus.UNKNOWN


def test_all_dimensions_are_always_present() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert set(result.dimensions) == {
        EffectivenessDimension.OUTCOME,
        EffectivenessDimension.QUALITY,
        EffectivenessDimension.PERFORMANCE,
        EffectivenessDimension.RELIABILITY,
    }


def test_evaluator_preserves_context_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    feedback = make_feedback(
        decision,
        signals=(FeedbackSignal.SUCCESS,),
    )

    result = DecisionEffectivenessEvaluator().evaluate(
        decision,
        feedback,
    )

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id


def test_evaluator_preserves_execution_id() -> None:
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-special",
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    result = DecisionEffectivenessEvaluator().evaluate(
        decision,
        feedback,
    )

    assert result.execution_id == "execution-special"


def test_context_mismatch_is_rejected() -> None:
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    with pytest.raises(
        ValueError,
        match="context_id must match",
    ):
        DecisionEffectivenessEvaluator().evaluate(
            decision,
            feedback,
        )


def test_correlation_mismatch_is_rejected() -> None:
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=decision.context_id,
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    with pytest.raises(
        ValueError,
        match="correlation_id must match",
    ):
        DecisionEffectivenessEvaluator().evaluate(
            decision,
            feedback,
        )


def test_invalid_decision_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(
        decision,
        signals=(FeedbackSignal.SUCCESS,),
    )

    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        DecisionEffectivenessEvaluator().evaluate(
            "invalid",
            feedback,
        )


def test_invalid_feedback_is_rejected() -> None:
    decision = make_decision()

    with pytest.raises(
        TypeError,
        match="feedback must be an ExecutionFeedback",
    ):
        DecisionEffectivenessEvaluator().evaluate(
            decision,
            "invalid",
        )


def test_success_reason_is_generated() -> None:
    result = evaluate((FeedbackSignal.SUCCESS,))

    assert "execution succeeded" in result.reasons


def test_failure_reason_is_generated() -> None:
    result = evaluate((FeedbackSignal.EXECUTION_FAILED,))

    assert "execution failed" in result.reasons


def test_retry_reason_is_generated() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        )
    )

    assert "execution required retries" in result.reasons


def test_fallback_reason_is_generated() -> None:
    result = evaluate(
        (
            FeedbackSignal.SUCCESS,
            FeedbackSignal.FALLBACK_USED,
        )
    )

    assert "execution required fallback behavior" in result.reasons


def test_reasons_have_deterministic_order() -> None:
    signals = (
        FeedbackSignal.SUCCESS,
        FeedbackSignal.FALLBACK_USED,
        FeedbackSignal.RETRY_OBSERVED,
        FeedbackSignal.PERFORMANCE_DEGRADED,
    )

    first = evaluate(signals)
    second = evaluate(signals)

    assert first.reasons == second.reasons
    assert first.reasons == (
        "execution performance was degraded",
        "execution required retries",
        "execution required fallback behavior",
        "execution succeeded",
    )


def test_evaluation_is_deterministic() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    feedback = make_feedback(
        decision,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
            FeedbackSignal.FALLBACK_USED,
        ),
    )

    evaluator = DecisionEffectivenessEvaluator()

    first = evaluator.evaluate(decision, feedback)
    second = evaluator.evaluate(decision, feedback)

    assert first == second


def test_evaluator_does_not_modify_decision() -> None:
    decision = make_decision()

    feedback = make_feedback(
        decision,
        signals=(FeedbackSignal.SUCCESS,),
    )

    before = decision

    DecisionEffectivenessEvaluator().evaluate(
        decision,
        feedback,
    )

    assert decision == before


def test_evaluator_does_not_modify_feedback() -> None:
    decision = make_decision()

    feedback = make_feedback(
        decision,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
    )

    before = feedback

    DecisionEffectivenessEvaluator().evaluate(
        decision,
        feedback,
    )

    assert feedback == before


def test_evaluator_has_no_runtime_action_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "switch_provider",
        "select_strategy",
        "adapt",
    }

    public_names = {
        name for name in dir(DecisionEffectivenessEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_exposes_only_evaluate_as_public_method() -> None:
    public_methods = {
        name for name in dir(DecisionEffectivenessEvaluator) if not name.startswith("_")
    }

    assert public_methods == {"evaluate"}
