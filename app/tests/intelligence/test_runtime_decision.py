"""Tests for the V10 RuntimeDecision contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from app.intelligence import ExecutionMode, RuntimeDecision


def make_ids() -> tuple[UUID, UUID]:
    return uuid4(), uuid4()


def test_runtime_decision_can_be_created() -> None:
    context_id, correlation_id = make_ids()

    decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert decision.mode is ExecutionMode.SEQUENTIAL
    assert decision.context_id == context_id
    assert decision.correlation_id == correlation_id
    assert decision.timeout_seconds == 60.0
    assert decision.max_workers == 1


def test_parallel_runtime_decision_accepts_multiple_workers() -> None:
    context_id, correlation_id = make_ids()

    decision = RuntimeDecision(
        mode=ExecutionMode.PARALLEL,
        context_id=context_id,
        correlation_id=correlation_id,
        max_workers=4,
    )

    assert decision.mode is ExecutionMode.PARALLEL
    assert decision.max_workers == 4


def test_create_preserves_runtime_constraints_and_provenance() -> None:
    context_id, correlation_id = make_ids()

    decision = RuntimeDecision.create(
        mode=ExecutionMode.PARALLEL,
        context_id=context_id,
        correlation_id=correlation_id,
        timeout_seconds=30.0,
        retry_enabled=True,
        max_retry_attempts=3,
        retry_delay_seconds=0.5,
        retry_exponential_backoff=True,
        fallback_allowed=False,
        max_workers=4,
        metadata={"source": "planner"},
    )

    assert decision.context_id == context_id
    assert decision.correlation_id == correlation_id
    assert decision.timeout_seconds == 30.0
    assert decision.retry_enabled is True
    assert decision.max_retry_attempts == 3
    assert decision.retry_delay_seconds == 0.5
    assert decision.retry_exponential_backoff is True
    assert decision.fallback_allowed is False
    assert decision.max_workers == 4
    assert decision.metadata["source"] == "planner"


def test_runtime_decision_is_frozen() -> None:
    context_id, correlation_id = make_ids()
    decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    with pytest.raises(FrozenInstanceError):
        decision.mode = ExecutionMode.PARALLEL  # type: ignore[misc]


def test_metadata_is_defensively_copied_and_immutable() -> None:
    context_id, correlation_id = make_ids()
    metadata = {"source": "planner"}

    decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert decision.metadata["source"] == "planner"

    with pytest.raises(TypeError):
        decision.metadata["source"] = "changed"  # type: ignore[index]


def test_timeout_must_be_positive() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="greater than 0"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            timeout_seconds=0,
        )


def test_retry_configuration_is_consistent() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="at least 1"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            retry_enabled=True,
            max_retry_attempts=0,
        )

    with pytest.raises(ValueError, match="must be 0"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            retry_enabled=False,
            max_retry_attempts=1,
        )


def test_retry_delay_cannot_be_negative() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="greater than or equal to 0"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            retry_delay_seconds=-0.1,
        )


def test_max_workers_must_be_positive() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="at least 1"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            max_workers=0,
        )


def test_sequential_mode_requires_one_worker() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="sequential"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            max_workers=2,
        )


def test_parallel_mode_requires_multiple_workers() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="parallel"):
        RuntimeDecision(
            mode=ExecutionMode.PARALLEL,
            context_id=context_id,
            correlation_id=correlation_id,
            max_workers=1,
        )


def test_invalid_mode_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(TypeError, match="ExecutionMode"):
        RuntimeDecision(
            mode="parallel",  # type: ignore[arg-type]
            context_id=context_id,
            correlation_id=correlation_id,
        )


def test_invalid_context_id_is_rejected() -> None:
    _, correlation_id = make_ids()

    with pytest.raises(TypeError, match="context_id must be a UUID"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id="context",  # type: ignore[arg-type]
            correlation_id=correlation_id,
        )


def test_invalid_correlation_id_is_rejected() -> None:
    context_id, _ = make_ids()

    with pytest.raises(TypeError, match="correlation_id must be a UUID"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id="correlation",  # type: ignore[arg-type]
        )


def test_created_at_is_timezone_aware() -> None:
    context_id, correlation_id = make_ids()

    decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert isinstance(decision.created_at, datetime)
    assert decision.created_at.tzinfo is not None


def test_naive_created_at_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="timezone-aware"):
        RuntimeDecision(
            mode=ExecutionMode.SEQUENTIAL,
            context_id=context_id,
            correlation_id=correlation_id,
            created_at=datetime.now(),
        )


def test_runtime_decision_contains_no_runtime_implementation_objects() -> None:
    context_id, correlation_id = make_ids()

    decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert not hasattr(decision, "executor")
    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "client")
    assert not hasattr(decision, "runtime")
    assert not hasattr(decision, "callback")


def test_distributed_mode_is_a_declarative_boundary_only() -> None:
    context_id, correlation_id = make_ids()

    decision = RuntimeDecision(
        mode=ExecutionMode.DISTRIBUTED,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert decision.mode is ExecutionMode.DISTRIBUTED
    assert decision.max_workers == 1
