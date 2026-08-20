"""Tests for the V10 execution feedback boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType
from uuid import uuid4

import pytest

from app.intelligence import (
    EvaluationResult,
    EvaluationStatus,
    ExecutionFeedback,
    ExecutionFeedbackBuilder,
    ExecutionObservation,
    ExecutionOutcome,
    FeedbackSignal,
)


def make_observation(
    *,
    execution_id: str = "execution-001",
    context_id=None,
    correlation_id=None,
    outcome: ExecutionOutcome = ExecutionOutcome.SUCCESS,
    duration_ms: float = 100.0,
    retry_count: int = 0,
    fallback_used: bool = False,
    error_type: str | None = None,
    error_message: str | None = None,
) -> ExecutionObservation:
    return ExecutionObservation.create(
        execution_id=execution_id,
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        outcome=outcome,
        duration_ms=duration_ms,
        retry_count=retry_count,
        fallback_used=fallback_used,
        error_type=error_type,
        error_message=error_message,
    )


def make_evaluation(
    observation: ExecutionObservation,
    *,
    status: EvaluationStatus = EvaluationStatus.PASS,
    dimensions=None,
    reasons: tuple[str, ...] = (),
) -> EvaluationResult:
    return EvaluationResult.create(
        execution_id=observation.execution_id,
        context_id=observation.context_id,
        correlation_id=observation.correlation_id,
        status=status,
        dimensions={} if dimensions is None else dimensions,
        reasons=reasons,
    )


def test_feedback_signal_values_are_stable() -> None:
    assert FeedbackSignal.SUCCESS.value == "success"
    assert FeedbackSignal.QUALITY_DEGRADED.value == "quality_degraded"
    assert FeedbackSignal.PERFORMANCE_DEGRADED.value == "performance_degraded"
    assert FeedbackSignal.RELIABILITY_DEGRADED.value == "reliability_degraded"
    assert FeedbackSignal.FALLBACK_USED.value == "fallback_used"
    assert FeedbackSignal.RETRY_OBSERVED.value == "retry_observed"
    assert FeedbackSignal.EXECUTION_FAILED.value == "execution_failed"
    assert FeedbackSignal.EXECUTION_PARTIAL.value == "execution_partial"
    assert FeedbackSignal.EXECUTION_CANCELLED.value == "execution_cancelled"
    assert FeedbackSignal.EVALUATION_UNKNOWN.value == "evaluation_unknown"


def test_feedback_accepts_valid_values() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
        reasons=("execution completed",),
    )

    assert feedback.execution_id == "execution-001"
    assert feedback.context_id == context_id
    assert feedback.correlation_id == correlation_id
    assert feedback.evaluation_status is EvaluationStatus.PASS
    assert feedback.signals == (FeedbackSignal.SUCCESS,)
    assert feedback.reasons == ("execution completed",)


def test_execution_id_must_be_string() -> None:
    with pytest.raises(TypeError, match="execution_id must be a string"):
        ExecutionFeedback.create(
            execution_id=123,
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
        )


def test_execution_id_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="execution_id must not be empty",
    ):
        ExecutionFeedback.create(
            execution_id="",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
        )


def test_evaluation_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="evaluation_status must be an EvaluationStatus",
    ):
        ExecutionFeedback.create(
            execution_id="execution-001",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status="pass",
        )


def test_signals_must_be_tuple() -> None:
    with pytest.raises(TypeError, match="signals must be a tuple"):
        ExecutionFeedback.create(
            execution_id="execution-001",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
            signals=[FeedbackSignal.SUCCESS],
        )


def test_signal_values_must_be_feedback_signals() -> None:
    with pytest.raises(
        TypeError,
        match="feedback signals must be FeedbackSignal values",
    ):
        ExecutionFeedback.create(
            execution_id="execution-001",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
            signals=("success",),
        )


def test_duplicate_signals_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="feedback signals must not contain duplicates",
    ):
        ExecutionFeedback.create(
            execution_id="execution-001",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
            signals=(
                FeedbackSignal.SUCCESS,
                FeedbackSignal.SUCCESS,
            ),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(TypeError, match="reasons must be a tuple"):
        ExecutionFeedback.create(
            execution_id="execution-001",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="feedback reasons must be strings",
    ):
        ExecutionFeedback.create(
            execution_id="execution-001",
            context_id=uuid4(),
            correlation_id=uuid4(),
            evaluation_status=EvaluationStatus.PASS,
            reasons=(123,),
        )


def test_metadata_is_mapping_proxy() -> None:
    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        metadata={"source": "test"},
    )

    assert isinstance(feedback.metadata, MappingProxyType)


def test_metadata_is_immutable() -> None:
    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        feedback.metadata["source"] = "changed"


def test_feedback_is_immutable() -> None:
    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
    )

    with pytest.raises(FrozenInstanceError):
        feedback.evaluation_status = EvaluationStatus.FAIL


def test_success_produces_success_signal() -> None:
    observation = make_observation()
    evaluation = make_evaluation(observation)

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert feedback.signals == (FeedbackSignal.SUCCESS,)


def test_failed_execution_produces_failed_signal() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.FAILED,
        error_type="TestError",
        error_message="test execution failure",
    )
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.FAIL,
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.EXECUTION_FAILED in feedback.signals


def test_partial_execution_produces_partial_signal() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.PARTIAL,
    )
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.EXECUTION_PARTIAL in feedback.signals


def test_cancelled_execution_produces_cancelled_signal() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.CANCELLED,
    )
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.FAIL,
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.EXECUTION_CANCELLED in feedback.signals


def test_quality_degradation_produces_quality_signal() -> None:
    observation = make_observation()
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        dimensions={
            "quality": EvaluationStatus.DEGRADED,
        },
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.QUALITY_DEGRADED in feedback.signals


def test_performance_degradation_produces_performance_signal() -> None:
    observation = make_observation()
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        dimensions={
            "performance": EvaluationStatus.DEGRADED,
        },
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.PERFORMANCE_DEGRADED in feedback.signals


def test_reliability_degradation_produces_reliability_signal() -> None:
    observation = make_observation()
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        dimensions={
            "reliability": EvaluationStatus.DEGRADED,
        },
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.RELIABILITY_DEGRADED in feedback.signals


def test_retry_produces_retry_signal() -> None:
    observation = make_observation(retry_count=2)
    evaluation = make_evaluation(observation)

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.RETRY_OBSERVED in feedback.signals


def test_zero_retries_do_not_produce_retry_signal() -> None:
    observation = make_observation(retry_count=0)
    evaluation = make_evaluation(observation)

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.RETRY_OBSERVED not in feedback.signals


def test_fallback_produces_fallback_signal() -> None:
    observation = make_observation(fallback_used=True)
    evaluation = make_evaluation(observation)

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.FALLBACK_USED in feedback.signals


def test_no_fallback_does_not_produce_fallback_signal() -> None:
    observation = make_observation(fallback_used=False)
    evaluation = make_evaluation(observation)

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.FALLBACK_USED not in feedback.signals


def test_unknown_evaluation_produces_unknown_signal() -> None:
    observation = make_observation()
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.UNKNOWN,
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert FeedbackSignal.EVALUATION_UNKNOWN in feedback.signals


def test_multiple_signals_are_supported() -> None:
    observation = make_observation(
        retry_count=2,
        fallback_used=True,
    )
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        dimensions={
            "performance": EvaluationStatus.DEGRADED,
            "reliability": EvaluationStatus.DEGRADED,
        },
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert feedback.signals == (
        FeedbackSignal.SUCCESS,
        FeedbackSignal.PERFORMANCE_DEGRADED,
        FeedbackSignal.RELIABILITY_DEGRADED,
        FeedbackSignal.RETRY_OBSERVED,
        FeedbackSignal.FALLBACK_USED,
    )


def test_signal_order_is_deterministic() -> None:
    observation = make_observation(
        retry_count=1,
        fallback_used=True,
    )
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        dimensions={
            "reliability": EvaluationStatus.DEGRADED,
            "performance": EvaluationStatus.DEGRADED,
        },
    )

    builder = ExecutionFeedbackBuilder()

    first = builder.build(observation, evaluation)
    second = builder.build(observation, evaluation)

    assert first.signals == second.signals


def test_feedback_preserves_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    observation = make_observation(
        context_id=context_id,
        correlation_id=correlation_id,
    )
    evaluation = make_evaluation(observation)

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert feedback.execution_id == observation.execution_id
    assert feedback.context_id == context_id
    assert feedback.correlation_id == correlation_id


def test_feedback_preserves_evaluation_status() -> None:
    observation = make_observation()
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert feedback.evaluation_status is EvaluationStatus.DEGRADED


def test_feedback_preserves_evaluation_reasons() -> None:
    observation = make_observation()
    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        reasons=("performance exceeded limit",),
    )

    feedback = ExecutionFeedbackBuilder().build(
        observation,
        evaluation,
    )

    assert feedback.reasons == ("performance exceeded limit",)


def test_observation_must_be_valid() -> None:
    observation = make_observation()
    evaluation = make_evaluation(observation)

    with pytest.raises(
        TypeError,
        match="observation must be an ExecutionObservation",
    ):
        ExecutionFeedbackBuilder().build(
            "invalid",
            evaluation,
        )


def test_evaluation_must_be_valid() -> None:
    observation = make_observation()

    with pytest.raises(
        TypeError,
        match="evaluation must be an EvaluationResult",
    ):
        ExecutionFeedbackBuilder().build(
            observation,
            "invalid",
        )


def test_mismatched_execution_id_is_rejected() -> None:
    observation = make_observation(
        execution_id="execution-A",
    )

    evaluation = EvaluationResult.create(
        execution_id="execution-B",
        context_id=observation.context_id,
        correlation_id=observation.correlation_id,
        status=EvaluationStatus.PASS,
    )

    with pytest.raises(
        ValueError,
        match="execution_id must match",
    ):
        ExecutionFeedbackBuilder().build(
            observation,
            evaluation,
        )


def test_mismatched_context_id_is_rejected() -> None:
    observation = make_observation()

    evaluation = EvaluationResult.create(
        execution_id=observation.execution_id,
        context_id=uuid4(),
        correlation_id=observation.correlation_id,
        status=EvaluationStatus.PASS,
    )

    with pytest.raises(
        ValueError,
        match="context_id must match",
    ):
        ExecutionFeedbackBuilder().build(
            observation,
            evaluation,
        )


def test_mismatched_correlation_id_is_rejected() -> None:
    observation = make_observation()

    evaluation = EvaluationResult.create(
        execution_id=observation.execution_id,
        context_id=observation.context_id,
        correlation_id=uuid4(),
        status=EvaluationStatus.PASS,
    )

    with pytest.raises(
        ValueError,
        match="correlation_id must match",
    ):
        ExecutionFeedbackBuilder().build(
            observation,
            evaluation,
        )


def test_builder_does_not_produce_action_signals() -> None:
    action_like_names = {
        "retry_execution",
        "switch_strategy",
        "change_provider",
        "replan",
    }

    assert not (action_like_names & {signal.value for signal in FeedbackSignal})


def test_builder_is_deterministic() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    observation = make_observation(
        context_id=context_id,
        correlation_id=correlation_id,
        retry_count=2,
        fallback_used=True,
    )

    evaluation = make_evaluation(
        observation,
        status=EvaluationStatus.DEGRADED,
        dimensions={
            "performance": EvaluationStatus.DEGRADED,
            "reliability": EvaluationStatus.DEGRADED,
        },
        reasons=("execution exceeded target",),
    )

    builder = ExecutionFeedbackBuilder()

    first = builder.build(observation, evaluation)
    second = builder.build(observation, evaluation)

    assert first == second
