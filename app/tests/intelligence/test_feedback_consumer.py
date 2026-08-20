"""Tests for the V10 intelligence feedback consumption boundary."""

from __future__ import annotations

from types import MappingProxyType
from uuid import uuid4

import pytest

from app.intelligence import (
    ExecutionFeedback,
    FeedbackConsumer,
    FeedbackSeverity,
    FeedbackSignal,
    IntelligenceFeedback,
    EvaluationStatus,
)


def make_feedback(
    *,
    signals: tuple[FeedbackSignal, ...] = (FeedbackSignal.SUCCESS,),
    execution_id: str = "execution-001",
    context_id=None,
    correlation_id=None,
) -> ExecutionFeedback:
    return ExecutionFeedback.create(
        execution_id=execution_id,
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        signals=signals,
    )


def test_consumer_returns_intelligence_feedback() -> None:
    feedback = make_feedback()

    result = FeedbackConsumer().consume(feedback)

    assert isinstance(result, IntelligenceFeedback)


def test_consumer_preserves_execution_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    feedback = make_feedback(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    result = FeedbackConsumer().consume(feedback)

    assert result.execution_id == feedback.execution_id
    assert result.context_id == context_id
    assert result.correlation_id == correlation_id


def test_consumer_preserves_signals() -> None:
    signals = (
        FeedbackSignal.SUCCESS,
        FeedbackSignal.RETRY_OBSERVED,
    )

    feedback = make_feedback(signals=signals)

    result = FeedbackConsumer().consume(feedback)

    assert result.signals == signals


def test_success_has_none_severity() -> None:
    feedback = make_feedback(
        signals=(FeedbackSignal.SUCCESS,),
    )

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.NONE


def test_unknown_evaluation_has_info_severity() -> None:
    feedback = make_feedback(
        signals=(FeedbackSignal.EVALUATION_UNKNOWN,),
    )

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.INFO


@pytest.mark.parametrize(
    "signal",
    [
        FeedbackSignal.RETRY_OBSERVED,
        FeedbackSignal.FALLBACK_USED,
        FeedbackSignal.QUALITY_DEGRADED,
        FeedbackSignal.PERFORMANCE_DEGRADED,
        FeedbackSignal.RELIABILITY_DEGRADED,
        FeedbackSignal.EXECUTION_PARTIAL,
    ],
)
def test_warning_signals_produce_warning_severity(
    signal: FeedbackSignal,
) -> None:
    feedback = make_feedback(signals=(signal,))

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.WARNING


@pytest.mark.parametrize(
    "signal",
    [
        FeedbackSignal.EXECUTION_FAILED,
        FeedbackSignal.EXECUTION_CANCELLED,
    ],
)
def test_critical_signals_produce_critical_severity(
    signal: FeedbackSignal,
) -> None:
    feedback = make_feedback(signals=(signal,))

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.CRITICAL


def test_highest_severity_wins() -> None:
    feedback = make_feedback(
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.PERFORMANCE_DEGRADED,
            FeedbackSignal.EXECUTION_FAILED,
        ),
    )

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.CRITICAL


def test_warning_beats_info() -> None:
    feedback = make_feedback(
        signals=(
            FeedbackSignal.EVALUATION_UNKNOWN,
            FeedbackSignal.FALLBACK_USED,
        ),
    )

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.WARNING


def test_consumer_is_deterministic() -> None:
    feedback = make_feedback(
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
            FeedbackSignal.FALLBACK_USED,
        ),
    )

    consumer = FeedbackConsumer()

    first = consumer.consume(feedback)
    second = consumer.consume(feedback)

    assert first == second


def test_intelligence_feedback_metadata_is_immutable() -> None:
    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
        metadata={"source": "test"},
    )

    result = FeedbackConsumer().consume(feedback)

    assert isinstance(result.metadata, MappingProxyType)

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_intelligence_feedback_is_immutable() -> None:
    feedback = make_feedback()

    result = FeedbackConsumer().consume(feedback)

    with pytest.raises(AttributeError):
        result.severity = FeedbackSeverity.CRITICAL


def test_consumer_rejects_invalid_feedback() -> None:
    with pytest.raises(
        TypeError,
        match="feedback must be an ExecutionFeedback",
    ):
        FeedbackConsumer().consume("invalid")


def test_empty_feedback_has_none_severity() -> None:
    feedback = make_feedback(signals=())

    result = FeedbackConsumer().consume(feedback)

    assert result.severity is FeedbackSeverity.NONE


def test_consumer_does_not_introduce_action_signals() -> None:
    action_like_names = {
        "retry_execution",
        "switch_strategy",
        "change_provider",
        "replan",
    }

    feedback = make_feedback(
        signals=(FeedbackSignal.EXECUTION_FAILED,),
    )

    result = FeedbackConsumer().consume(feedback)

    assert not (action_like_names & {signal.value for signal in result.signals})


def test_consumer_does_not_modify_input_feedback() -> None:
    feedback = make_feedback(
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.FALLBACK_USED,
        ),
    )

    before = feedback

    result = FeedbackConsumer().consume(feedback)

    assert feedback == before
    assert result.execution_id == before.execution_id


def test_feedback_consumer_has_no_runtime_action_interface() -> None:
    public_methods = {
        name for name in dir(FeedbackConsumer) if not name.startswith("_")
    }

    assert public_methods == {"consume"}
