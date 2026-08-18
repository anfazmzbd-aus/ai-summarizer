"""Tests for the V10 TaskDecision contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from app.intelligence import TaskAction, TaskDecision


def make_ids() -> tuple[UUID, UUID]:
    return uuid4(), uuid4()


def test_task_decision_can_be_created() -> None:
    context_id, correlation_id = make_ids()

    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert decision.action is TaskAction.SUMMARIZE
    assert decision.context_id == context_id
    assert decision.correlation_id == correlation_id


def test_task_decision_create_preserves_provenance() -> None:
    context_id, correlation_id = make_ids()

    decision = TaskDecision.create(
        action=TaskAction.RETRIEVE,
        context_id=context_id,
        correlation_id=correlation_id,
        reason="Additional evidence is required.",
        confidence=0.8,
    )

    assert decision.context_id == context_id
    assert decision.correlation_id == correlation_id
    assert decision.reason == "Additional evidence is required."
    assert decision.confidence == 0.8


def test_all_supported_actions_are_explicit() -> None:
    assert {action.value for action in TaskAction} == {
        "summarize",
        "retrieve",
        "verify",
        "refine",
        "retry",
        "fallback",
        "abort",
    }


def test_task_decision_is_frozen() -> None:
    context_id, correlation_id = make_ids()
    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    with pytest.raises(FrozenInstanceError):
        decision.action = TaskAction.ABORT  # type: ignore[misc]


def test_metadata_is_defensively_copied() -> None:
    context_id, correlation_id = make_ids()
    metadata = {"source": "planner"}

    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert decision.metadata["source"] == "planner"


def test_metadata_is_immutable() -> None:
    context_id, correlation_id = make_ids()
    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
        metadata={"source": "planner"},
    )

    with pytest.raises(TypeError):
        decision.metadata["source"] = "changed"  # type: ignore[index]


def test_confidence_must_be_within_range() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        TaskDecision(
            action=TaskAction.SUMMARIZE,
            context_id=context_id,
            correlation_id=correlation_id,
            confidence=1.1,
        )

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        TaskDecision(
            action=TaskAction.SUMMARIZE,
            context_id=context_id,
            correlation_id=correlation_id,
            confidence=-0.1,
        )


def test_invalid_action_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(TypeError, match="action must be a TaskAction"):
        TaskDecision(
            action="summarize",  # type: ignore[arg-type]
            context_id=context_id,
            correlation_id=correlation_id,
        )


def test_invalid_context_id_is_rejected() -> None:
    _, correlation_id = make_ids()

    with pytest.raises(TypeError, match="context_id must be a UUID"):
        TaskDecision(
            action=TaskAction.SUMMARIZE,
            context_id="context",  # type: ignore[arg-type]
            correlation_id=correlation_id,
        )


def test_invalid_correlation_id_is_rejected() -> None:
    context_id, _ = make_ids()

    with pytest.raises(TypeError, match="correlation_id must be a UUID"):
        TaskDecision(
            action=TaskAction.SUMMARIZE,
            context_id=context_id,
            correlation_id="correlation",  # type: ignore[arg-type]
        )


def test_invalid_confidence_type_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(TypeError, match="confidence must be a number"):
        TaskDecision(
            action=TaskAction.SUMMARIZE,
            context_id=context_id,
            correlation_id=correlation_id,
            confidence="high",  # type: ignore[arg-type]
        )


def test_created_at_is_timezone_aware() -> None:
    context_id, correlation_id = make_ids()
    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert isinstance(decision.created_at, datetime)
    assert decision.created_at.tzinfo is not None


def test_naive_created_at_is_rejected() -> None:
    context_id, correlation_id = make_ids()

    with pytest.raises(ValueError, match="timezone-aware"):
        TaskDecision(
            action=TaskAction.SUMMARIZE,
            context_id=context_id,
            correlation_id=correlation_id,
            created_at=datetime.now(),
        )


def test_task_decision_is_provider_independent() -> None:
    context_id, correlation_id = make_ids()

    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "client")
    assert not hasattr(decision, "runtime")
