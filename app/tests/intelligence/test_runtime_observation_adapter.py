"""Tests for the V10 runtime observation adapter."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    ExecutionObservation,
    ExecutionOutcome,
    RuntimeObservationAdapter,
)


def make_adapter() -> RuntimeObservationAdapter:
    return RuntimeObservationAdapter()


def make_ids():
    return uuid4(), uuid4()


def test_adapter_creates_success_observation() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
    )

    assert isinstance(observation, ExecutionObservation)
    assert observation.outcome is ExecutionOutcome.SUCCESS
    assert observation.execution_id == "execution-001"
    assert observation.context_id == context_id
    assert observation.correlation_id == correlation_id


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("success", ExecutionOutcome.SUCCESS),
        ("succeeded", ExecutionOutcome.SUCCESS),
        ("completed", ExecutionOutcome.SUCCESS),
        ("complete", ExecutionOutcome.SUCCESS),
        ("failed", ExecutionOutcome.FAILED),
        ("failure", ExecutionOutcome.FAILED),
        ("cancelled", ExecutionOutcome.CANCELLED),
        ("canceled", ExecutionOutcome.CANCELLED),
        ("partial", ExecutionOutcome.PARTIAL),
    ],
)
def test_adapter_maps_runtime_status(
    status: str,
    expected: ExecutionOutcome,
) -> None:
    context_id, correlation_id = make_ids()

    error = RuntimeError("failed") if expected is ExecutionOutcome.FAILED else None

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status=status,
        error=error,
    )

    assert observation.outcome is expected


def test_status_mapping_is_case_insensitive() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="  SUCCESS ",
    )

    assert observation.outcome is ExecutionOutcome.SUCCESS


def test_unsupported_status_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(
        ValueError,
        match="unsupported runtime execution status",
    ):
        make_adapter().observe(
            execution_id="execution-001",
            context_id=context_id,
            correlation_id=correlation_id,
            status="running",
        )


def test_status_must_be_string() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(TypeError, match="status must be a string"):
        make_adapter().observe(
            execution_id="execution-001",
            context_id=context_id,
            correlation_id=correlation_id,
            status=1,
        )


def test_adapter_preserves_duration() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
        duration_ms=321.5,
    )

    assert observation.duration_ms == 321.5


def test_adapter_preserves_retry_count() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
        retry_count=3,
    )

    assert observation.retry_count == 3


def test_adapter_preserves_fallback_flag() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
        fallback_used=True,
    )

    assert observation.fallback_used is True


def test_exception_is_normalized_without_exposing_exception_object() -> None:
    context_id, correlation_id = make_ids()
    error = TimeoutError("execution timed out")

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="failed",
        error=error,
    )

    assert observation.error_type == "TimeoutError"
    assert observation.error_message == "execution timed out"


def test_string_error_is_normalized() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="failed",
        error="provider unavailable",
    )

    assert observation.error_type == "RuntimeError"
    assert observation.error_message == "provider unavailable"


def test_none_error_remains_none() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
    )

    assert observation.error_type is None
    assert observation.error_message is None


def test_invalid_error_type_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(
        TypeError,
        match="error must be an exception, string, or None",
    ):
        make_adapter().observe(
            execution_id="execution-001",
            context_id=context_id,
            correlation_id=correlation_id,
            status="success",
            error=123,
        )


def test_metadata_is_forwarded() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
        metadata={
            "layer_count": 3,
            "source": "runtime",
        },
    )

    assert observation.metadata["layer_count"] == 3
    assert observation.metadata["source"] == "runtime"


def test_metadata_remains_observation_data_only() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
        metadata={"source": "runtime"},
    )

    assert observation.metadata["source"] == "runtime"
    assert "execution_engine" not in observation.metadata


def test_adapter_preserves_provenance() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
    )

    assert observation.context_id == context_id
    assert observation.correlation_id == correlation_id
    assert observation.execution_id == "execution-001"


def test_aggregate_retry_count_from_empty_nodes() -> None:
    assert RuntimeObservationAdapter.aggregate_retry_count([]) == 0


def test_aggregate_retry_count_from_runtime_nodes() -> None:
    class NodeState:
        def __init__(self, retries: int) -> None:
            self.retries = retries

    nodes = [
        NodeState(0),
        NodeState(2),
        NodeState(1),
    ]

    assert RuntimeObservationAdapter.aggregate_retry_count(nodes) == 3


def test_aggregate_retry_count_ignores_missing_retry_attribute() -> None:
    class NodeState:
        pass

    assert RuntimeObservationAdapter.aggregate_retry_count([NodeState()]) == 0


def test_aggregate_retry_count_rejects_invalid_retry_value() -> None:
    class NodeState:
        retries = "2"

    with pytest.raises(
        TypeError,
        match="runtime node retries must be integers",
    ):
        RuntimeObservationAdapter.aggregate_retry_count([NodeState()])


def test_aggregate_retry_count_rejects_negative_retry_value() -> None:
    class NodeState:
        retries = -1

    with pytest.raises(
        ValueError,
        match="runtime node retries must be non-negative",
    ):
        RuntimeObservationAdapter.aggregate_retry_count([NodeState()])


def test_adapter_does_not_return_runtime_object() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="success",
    )

    assert type(observation) is ExecutionObservation
    assert not hasattr(observation, "execution_context")
    assert not hasattr(observation, "execution_engine")
    assert not hasattr(observation, "runtime_manager")


def test_failed_runtime_status_produces_failed_observation() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="failed",
        error=ValueError("invalid input"),
    )

    assert observation.outcome is ExecutionOutcome.FAILED
    assert observation.error_type == "ValueError"
    assert observation.error_message == "invalid input"


def test_cancelled_runtime_status_does_not_require_error() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="cancelled",
    )

    assert observation.outcome is ExecutionOutcome.CANCELLED
    assert observation.error_type is None


def test_partial_runtime_status_does_not_require_error() -> None:
    context_id, correlation_id = make_ids()

    observation = make_adapter().observe(
        execution_id="execution-001",
        context_id=context_id,
        correlation_id=correlation_id,
        status="partial",
    )

    assert observation.outcome is ExecutionOutcome.PARTIAL
