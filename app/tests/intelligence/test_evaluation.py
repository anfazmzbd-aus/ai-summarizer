"""Tests for the V10 deterministic execution evaluator."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    EvaluationCriteria,
    EvaluationResult,
    EvaluationStatus,
    ExecutionEvaluator,
    ExecutionObservation,
    ExecutionOutcome,
)


def make_observation(
    *,
    outcome: ExecutionOutcome = ExecutionOutcome.SUCCESS,
    duration_ms: float = 100.0,
    retry_count: int = 0,
    fallback_used: bool = False,
    error_type: str | None = None,
    error_message: str | None = None,
) -> ExecutionObservation:
    if outcome is ExecutionOutcome.FAILED:
        error_type = error_type or "RuntimeError"
        error_message = error_message or "execution failed"

    return ExecutionObservation.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=uuid4(),
        outcome=outcome,
        duration_ms=duration_ms,
        retry_count=retry_count,
        fallback_used=fallback_used,
        error_type=error_type,
        error_message=error_message,
    )


def test_criteria_accepts_defaults() -> None:
    criteria = EvaluationCriteria()

    assert criteria.require_success is True
    assert criteria.max_duration_ms is None
    assert criteria.max_retries is None
    assert criteria.allow_fallback is True


def test_criteria_rejects_invalid_require_success() -> None:
    with pytest.raises(
        TypeError,
        match="require_success must be a bool",
    ):
        EvaluationCriteria(require_success=1)


def test_criteria_rejects_negative_duration() -> None:
    with pytest.raises(
        ValueError,
        match="max_duration_ms must be greater than or equal to 0",
    ):
        EvaluationCriteria(max_duration_ms=-1)


def test_criteria_rejects_invalid_duration() -> None:
    with pytest.raises(
        TypeError,
        match="max_duration_ms must be a number or None",
    ):
        EvaluationCriteria(max_duration_ms="100")


def test_criteria_rejects_boolean_duration() -> None:
    with pytest.raises(
        TypeError,
        match="max_duration_ms must be a number or None",
    ):
        EvaluationCriteria(max_duration_ms=True)


def test_criteria_rejects_negative_retries() -> None:
    with pytest.raises(
        ValueError,
        match="max_retries must be greater than or equal to 0",
    ):
        EvaluationCriteria(max_retries=-1)


def test_criteria_rejects_invalid_retries() -> None:
    with pytest.raises(
        TypeError,
        match="max_retries must be an integer or None",
    ):
        EvaluationCriteria(max_retries=1.5)


def test_criteria_rejects_boolean_retries() -> None:
    with pytest.raises(
        TypeError,
        match="max_retries must be an integer or None",
    ):
        EvaluationCriteria(max_retries=True)


def test_criteria_rejects_invalid_allow_fallback() -> None:
    with pytest.raises(
        TypeError,
        match="allow_fallback must be a bool",
    ):
        EvaluationCriteria(allow_fallback=1)


def test_success_with_no_constraints_has_unknown_non_outcome_dimensions() -> None:
    observation = make_observation()
    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(),
    )

    assert result.status is EvaluationStatus.UNKNOWN
    assert result.dimensions["outcome"] is EvaluationStatus.PASS
    assert result.dimensions["performance"] is EvaluationStatus.UNKNOWN
    assert result.dimensions["reliability"] is EvaluationStatus.UNKNOWN


def test_success_meeting_all_constraints_passes() -> None:
    observation = make_observation(
        duration_ms=100,
        retry_count=1,
        fallback_used=False,
    )

    criteria = EvaluationCriteria(
        require_success=True,
        max_duration_ms=200,
        max_retries=2,
        allow_fallback=True,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        criteria,
    )

    assert result.status is EvaluationStatus.PASS
    assert result.dimensions["outcome"] is EvaluationStatus.PASS
    assert result.dimensions["performance"] is EvaluationStatus.PASS
    assert result.dimensions["reliability"] is EvaluationStatus.PASS
    assert result.reasons == ()


def test_failed_execution_fails_when_success_required() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.FAILED,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(require_success=True),
    )

    assert result.status is EvaluationStatus.FAIL
    assert result.dimensions["outcome"] is EvaluationStatus.FAIL
    assert "execution failed" in result.reasons


def test_failed_execution_is_degraded_when_success_not_required() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.FAILED,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(require_success=False),
    )

    assert result.status is EvaluationStatus.DEGRADED
    assert result.dimensions["outcome"] is EvaluationStatus.DEGRADED


def test_cancelled_execution_fails() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.CANCELLED,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(),
    )

    assert result.status is EvaluationStatus.FAIL
    assert result.dimensions["outcome"] is EvaluationStatus.FAIL


def test_partial_execution_is_degraded() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.PARTIAL,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(),
    )

    assert result.status is EvaluationStatus.DEGRADED
    assert result.dimensions["outcome"] is EvaluationStatus.DEGRADED


def test_duration_at_limit_passes() -> None:
    observation = make_observation(duration_ms=100)

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(max_duration_ms=100),
    )

    assert result.dimensions["performance"] is EvaluationStatus.PASS


def test_duration_over_limit_is_degraded() -> None:
    observation = make_observation(duration_ms=101)

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(max_duration_ms=100),
    )

    assert result.status is EvaluationStatus.DEGRADED
    assert result.dimensions["performance"] is EvaluationStatus.DEGRADED
    assert "duration exceeded" in result.reasons[0]


def test_retry_count_at_limit_passes() -> None:
    observation = make_observation(retry_count=2)

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(max_retries=2),
    )

    assert result.dimensions["reliability"] is EvaluationStatus.PASS


def test_retry_count_over_limit_is_degraded() -> None:
    observation = make_observation(retry_count=3)

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(max_retries=2),
    )

    assert result.status is EvaluationStatus.DEGRADED
    assert result.dimensions["reliability"] is EvaluationStatus.DEGRADED


def test_fallback_allowed_passes_reliability_when_retry_limit_exists() -> None:
    observation = make_observation(
        fallback_used=True,
        retry_count=1,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(
            max_retries=2,
            allow_fallback=True,
        ),
    )

    assert result.dimensions["reliability"] is EvaluationStatus.PASS


def test_fallback_not_allowed_is_degraded() -> None:
    observation = make_observation(fallback_used=True)

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(allow_fallback=False),
    )

    assert result.status is EvaluationStatus.DEGRADED
    assert result.dimensions["reliability"] is EvaluationStatus.DEGRADED
    assert "fallback execution was not allowed" in result.reasons


def test_failure_has_precedence_over_degraded_dimensions() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.FAILED,
        duration_ms=500,
    )

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(
            require_success=True,
            max_duration_ms=100,
        ),
    )

    assert result.status is EvaluationStatus.FAIL


def test_degraded_has_precedence_over_unknown_dimensions() -> None:
    observation = make_observation(duration_ms=500)

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(max_duration_ms=100),
    )

    assert result.status is EvaluationStatus.DEGRADED


def test_evaluation_preserves_provenance() -> None:
    observation = make_observation()

    result = ExecutionEvaluator().evaluate(
        observation,
        EvaluationCriteria(),
    )

    assert result.execution_id == observation.execution_id
    assert result.context_id == observation.context_id
    assert result.correlation_id == observation.correlation_id


def test_evaluation_returns_evaluation_result() -> None:
    result = ExecutionEvaluator().evaluate(
        make_observation(),
        EvaluationCriteria(),
    )

    assert isinstance(result, EvaluationResult)


def test_evaluation_is_deterministic() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    observation = ExecutionObservation.create(
        execution_id="execution-deterministic",
        context_id=context_id,
        correlation_id=correlation_id,
        outcome=ExecutionOutcome.SUCCESS,
        duration_ms=100,
        retry_count=1,
        fallback_used=False,
    )

    criteria = EvaluationCriteria(
        max_duration_ms=200,
        max_retries=2,
        allow_fallback=True,
    )

    evaluator = ExecutionEvaluator()

    first = evaluator.evaluate(observation, criteria)
    second = evaluator.evaluate(observation, criteria)

    assert first == second


def test_evaluator_rejects_invalid_observation() -> None:
    with pytest.raises(
        TypeError,
        match="observation must be an ExecutionObservation",
    ):
        ExecutionEvaluator().evaluate(
            "invalid",
            EvaluationCriteria(),
        )


def test_evaluator_rejects_invalid_criteria() -> None:
    with pytest.raises(
        TypeError,
        match="criteria must be an EvaluationCriteria",
    ):
        ExecutionEvaluator().evaluate(
            make_observation(),
            "invalid",
        )
