"""Tests for the V10 ExecutionObservation contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType
from uuid import uuid4

import pytest

from app.intelligence import ExecutionObservation, ExecutionOutcome


def make_observation(
    *,
    outcome: ExecutionOutcome = ExecutionOutcome.SUCCESS,
    **overrides,
) -> ExecutionObservation:
    """Create a valid observation for test cases."""

    values = {
        "execution_id": "execution-001",
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "outcome": outcome,
        "duration_ms": 125.5,
        "retry_count": 1,
        "fallback_used": False,
        "metadata": {"source": "test"},
    }

    if outcome is ExecutionOutcome.FAILED:
        values["error_type"] = "RuntimeError"
        values["error_message"] = "execution failed"

    values.update(overrides)

    return ExecutionObservation(**values)


def test_execution_outcome_values() -> None:
    assert ExecutionOutcome.SUCCESS.value == "success"
    assert ExecutionOutcome.FAILED.value == "failed"
    assert ExecutionOutcome.CANCELLED.value == "cancelled"
    assert ExecutionOutcome.PARTIAL.value == "partial"


def test_observation_accepts_valid_success() -> None:
    observation = make_observation()

    assert observation.execution_id == "execution-001"
    assert observation.outcome is ExecutionOutcome.SUCCESS
    assert observation.duration_ms == 125.5
    assert observation.retry_count == 1
    assert observation.fallback_used is False


def test_observation_accepts_valid_failure() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.FAILED,
        error_type="TimeoutError",
        error_message="execution timed out",
    )

    assert observation.outcome is ExecutionOutcome.FAILED
    assert observation.error_type == "TimeoutError"
    assert observation.error_message == "execution timed out"


def test_observation_accepts_cancelled_without_error() -> None:
    observation = make_observation(outcome=ExecutionOutcome.CANCELLED)

    assert observation.outcome is ExecutionOutcome.CANCELLED
    assert observation.error_type is None
    assert observation.error_message is None


def test_observation_accepts_partial_without_error() -> None:
    observation = make_observation(outcome=ExecutionOutcome.PARTIAL)

    assert observation.outcome is ExecutionOutcome.PARTIAL


def test_execution_id_must_be_string() -> None:
    with pytest.raises(TypeError, match="execution_id must be a string"):
        make_observation(execution_id=123)


def test_execution_id_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="execution_id must not be empty"):
        make_observation(execution_id="")


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(TypeError, match="context_id must be a UUID"):
        make_observation(context_id="context-001")


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(TypeError, match="correlation_id must be a UUID"):
        make_observation(correlation_id="correlation-001")


def test_outcome_must_be_execution_outcome() -> None:
    with pytest.raises(TypeError, match="outcome must be an ExecutionOutcome"):
        make_observation(outcome="success")


@pytest.mark.parametrize("value", [-1, -0.1])
def test_duration_must_be_non_negative(value: float) -> None:
    with pytest.raises(
        ValueError,
        match="duration_ms must be greater than or equal to 0",
    ):
        make_observation(duration_ms=value)


def test_duration_must_be_numeric() -> None:
    with pytest.raises(TypeError, match="duration_ms must be a number"):
        make_observation(duration_ms="100")


def test_duration_rejects_boolean() -> None:
    with pytest.raises(TypeError, match="duration_ms must be a number"):
        make_observation(duration_ms=True)


def test_retry_count_must_be_integer() -> None:
    with pytest.raises(TypeError, match="retry_count must be an integer"):
        make_observation(retry_count=1.5)


def test_retry_count_rejects_boolean() -> None:
    with pytest.raises(TypeError, match="retry_count must be an integer"):
        make_observation(retry_count=True)


def test_retry_count_must_be_non_negative() -> None:
    with pytest.raises(
        ValueError,
        match="retry_count must be greater than or equal to 0",
    ):
        make_observation(retry_count=-1)


def test_fallback_used_must_be_boolean() -> None:
    with pytest.raises(TypeError, match="fallback_used must be a bool"):
        make_observation(fallback_used=1)


def test_error_type_must_be_string_or_none() -> None:
    with pytest.raises(TypeError, match="error_type must be a string or None"):
        make_observation(error_type=123)


def test_error_message_must_be_string_or_none() -> None:
    with pytest.raises(TypeError, match="error_message must be a string or None"):
        make_observation(error_message=123)


def test_failed_outcome_requires_error_type() -> None:
    with pytest.raises(
        ValueError,
        match="error_type must be provided when outcome is FAILED",
    ):
        make_observation(
            outcome=ExecutionOutcome.FAILED,
            error_type=None,
            error_message="execution failed",
        )


def test_failed_outcome_requires_error_message() -> None:
    with pytest.raises(
        ValueError,
        match="error_message must be provided when outcome is FAILED",
    ):
        make_observation(
            outcome=ExecutionOutcome.FAILED,
            error_type="RuntimeError",
            error_message=None,
        )


def test_non_failed_outcome_can_have_error_information() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.PARTIAL,
        error_type="PartialExecutionError",
        error_message="some nodes failed",
    )

    assert observation.error_type == "PartialExecutionError"
    assert observation.error_message == "some nodes failed"


def test_metadata_must_be_mapping() -> None:
    with pytest.raises(TypeError, match="metadata must be a mapping"):
        make_observation(metadata=["invalid"])


def test_metadata_is_stored_as_mapping_proxy() -> None:
    observation = make_observation(metadata={"source": "test"})

    assert isinstance(observation.metadata, MappingProxyType)
    assert observation.metadata["source"] == "test"


def test_metadata_is_copied_from_input_mapping() -> None:
    metadata = {"source": "test"}
    observation = make_observation(metadata=metadata)

    metadata["source"] = "changed"

    assert observation.metadata["source"] == "test"


def test_metadata_is_immutable() -> None:
    observation = make_observation(metadata={"source": "test"})

    with pytest.raises(TypeError):
        observation.metadata["source"] = "changed"


def test_observation_is_immutable() -> None:
    observation = make_observation()

    with pytest.raises(FrozenInstanceError):
        observation.outcome = ExecutionOutcome.FAILED


def test_create_factory_preserves_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    observation = ExecutionObservation.create(
        execution_id="execution-123",
        context_id=context_id,
        correlation_id=correlation_id,
        outcome=ExecutionOutcome.SUCCESS,
    )

    assert observation.execution_id == "execution-123"
    assert observation.context_id == context_id
    assert observation.correlation_id == correlation_id


def test_create_factory_accepts_metadata() -> None:
    observation = ExecutionObservation.create(
        execution_id="execution-123",
        context_id=uuid4(),
        correlation_id=uuid4(),
        outcome=ExecutionOutcome.SUCCESS,
        metadata={"component": "test"},
    )

    assert observation.metadata["component"] == "test"


def test_create_factory_defaults_metadata_to_empty_mapping() -> None:
    observation = ExecutionObservation.create(
        execution_id="execution-123",
        context_id=uuid4(),
        correlation_id=uuid4(),
        outcome=ExecutionOutcome.SUCCESS,
    )

    assert observation.metadata == {}


def test_provenance_ids_are_preserved_independently() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    observation = make_observation(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert observation.context_id is context_id
    assert observation.correlation_id is correlation_id
    assert observation.context_id != observation.correlation_id


def test_runtime_objects_are_not_required() -> None:
    observation = make_observation()

    assert observation.execution_id
    assert observation.context_id
    assert observation.correlation_id
    assert observation.outcome


def test_observation_contains_no_provider_or_executor_state() -> None:
    observation = make_observation()

    field_names = set(observation.__dataclass_fields__)

    assert "provider" not in field_names
    assert "provider_client" not in field_names
    assert "executor" not in field_names
    assert "runtime" not in field_names
    assert "callback" not in field_names


def test_success_observation_can_record_retries() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.SUCCESS,
        retry_count=2,
    )

    assert observation.retry_count == 2


def test_success_observation_can_record_fallback() -> None:
    observation = make_observation(
        outcome=ExecutionOutcome.SUCCESS,
        fallback_used=True,
    )

    assert observation.fallback_used is True
