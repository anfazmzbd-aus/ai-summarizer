"""Tests for the V10 ProvenanceContext contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime
import json
from uuid import UUID, uuid4

import pytest

from app.intelligence import ProvenanceContext


def make_ids() -> dict[str, UUID]:
    return {
        "context_id": uuid4(),
        "task_decision_id": uuid4(),
        "plan_id": uuid4(),
        "execution_id": uuid4(),
        "evaluation_id": uuid4(),
        "adaptation_id": uuid4(),
        "parent_correlation_id": uuid4(),
    }


def test_provenance_context_creates_root_correlation_id() -> None:
    provenance = ProvenanceContext.create()

    assert isinstance(provenance.correlation_id, UUID)
    assert provenance.context_id is None
    assert provenance.execution_id is None


def test_create_preserves_all_lifecycle_ids() -> None:
    ids = make_ids()

    provenance = ProvenanceContext.create(**ids)

    for name, value in ids.items():
        assert getattr(provenance, name) == value


def test_provenance_context_is_frozen() -> None:
    provenance = ProvenanceContext.create()

    with pytest.raises(FrozenInstanceError):
        provenance.correlation_id = uuid4()  # type: ignore[misc]


def test_created_at_is_timezone_aware() -> None:
    provenance = ProvenanceContext.create()

    assert isinstance(provenance.created_at, datetime)
    assert provenance.created_at.tzinfo is not None


def test_naive_created_at_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ProvenanceContext(created_at=datetime.now())


def test_ids_must_be_uuid_values() -> None:
    with pytest.raises(TypeError, match="execution_id must be a UUID"):
        ProvenanceContext(execution_id="execution")  # type: ignore[arg-type]


def test_to_dict_is_json_safe() -> None:
    ids = make_ids()
    provenance = ProvenanceContext.create(**ids)

    data = provenance.to_dict()

    assert data["correlation_id"] == str(provenance.correlation_id)
    assert data["execution_id"] == str(ids["execution_id"])

    assert all(value is None or isinstance(value, str) for value in data.values())


def test_to_json_is_valid_json() -> None:
    provenance = ProvenanceContext.create(
        execution_id=uuid4(),
    )

    payload = json.loads(provenance.to_json())

    assert payload["correlation_id"] == str(provenance.correlation_id)
    assert payload["execution_id"] == str(provenance.execution_id)


def test_to_json_is_canonical_and_deterministically_ordered() -> None:
    correlation_id = uuid4()
    execution_id = uuid4()

    created_at = datetime.now().astimezone()

    first = ProvenanceContext(
        correlation_id=correlation_id,
        execution_id=execution_id,
        created_at=created_at,
    )

    second = ProvenanceContext(
        correlation_id=correlation_id,
        execution_id=execution_id,
        created_at=created_at,
    )

    assert first.to_json() == second.to_json()


def test_existing_v9_execution_id_is_referenced_not_replaced() -> None:
    execution_id = uuid4()

    provenance = ProvenanceContext.create(
        execution_id=execution_id,
    )

    assert provenance.execution_id == execution_id
    assert provenance.correlation_id != execution_id


def test_parent_correlation_supports_nested_lifecycles() -> None:
    parent = ProvenanceContext.create()

    child = ProvenanceContext.create(
        parent_correlation_id=parent.correlation_id,
    )

    assert child.parent_correlation_id == parent.correlation_id
    assert child.correlation_id != parent.correlation_id


def test_future_evaluation_and_adaptation_slots_are_optional() -> None:
    provenance = ProvenanceContext.create()

    assert provenance.evaluation_id is None
    assert provenance.adaptation_id is None


def test_provenance_context_has_no_runtime_or_provider_dependency() -> None:
    provenance = ProvenanceContext.create()

    assert not hasattr(provenance, "runtime")
    assert not hasattr(provenance, "provider")
    assert not hasattr(provenance, "client")
    assert not hasattr(provenance, "executor")


def test_round_trip_ids_remain_identifiable_in_serialized_output() -> None:
    execution_id = uuid4()
    evaluation_id = uuid4()

    provenance = ProvenanceContext.create(
        execution_id=execution_id,
        evaluation_id=evaluation_id,
    )

    payload = json.loads(provenance.to_json())

    assert UUID(payload["execution_id"]) == execution_id
    assert UUID(payload["evaluation_id"]) == evaluation_id
