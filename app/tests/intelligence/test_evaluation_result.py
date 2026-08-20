"""Tests for the V10 EvaluationResult contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType
from uuid import uuid4

import pytest

from app.intelligence import EvaluationResult, EvaluationStatus


def make_result(**overrides) -> EvaluationResult:
    values = {
        "execution_id": "execution-001",
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "status": EvaluationStatus.PASS,
        "dimensions": {
            "outcome": EvaluationStatus.PASS,
        },
        "reasons": (),
        "metadata": {"source": "test"},
    }
    values.update(overrides)
    return EvaluationResult(**values)


def test_result_accepts_valid_values() -> None:
    result = make_result()

    assert result.execution_id == "execution-001"
    assert result.status is EvaluationStatus.PASS
    assert result.dimensions["outcome"] is EvaluationStatus.PASS


def test_evaluation_status_values() -> None:
    assert EvaluationStatus.PASS.value == "pass"
    assert EvaluationStatus.FAIL.value == "fail"
    assert EvaluationStatus.DEGRADED.value == "degraded"
    assert EvaluationStatus.UNKNOWN.value == "unknown"


def test_execution_id_must_be_string() -> None:
    with pytest.raises(TypeError, match="execution_id must be a string"):
        make_result(execution_id=123)


def test_execution_id_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="execution_id must not be empty"):
        make_result(execution_id="")


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(TypeError, match="context_id must be a UUID"):
        make_result(context_id="context")


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(TypeError, match="correlation_id must be a UUID"):
        make_result(correlation_id="correlation")


def test_status_must_be_evaluation_status() -> None:
    with pytest.raises(TypeError, match="status must be an EvaluationStatus"):
        make_result(status="pass")


def test_dimensions_must_be_mapping() -> None:
    with pytest.raises(TypeError, match="dimensions must be a mapping"):
        make_result(dimensions=[])


def test_dimension_name_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="dimension names must be strings",
    ):
        make_result(dimensions={1: EvaluationStatus.PASS})


def test_dimension_name_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="dimension names must not be empty",
    ):
        make_result(dimensions={"": EvaluationStatus.PASS})


def test_dimension_value_must_be_evaluation_status() -> None:
    with pytest.raises(
        TypeError,
        match="dimension values must be EvaluationStatus values",
    ):
        make_result(dimensions={"outcome": "pass"})


def test_dimensions_are_mapping_proxy() -> None:
    result = make_result()

    assert isinstance(result.dimensions, MappingProxyType)


def test_dimensions_are_copied() -> None:
    dimensions = {"outcome": EvaluationStatus.PASS}
    result = make_result(dimensions=dimensions)

    dimensions["outcome"] = EvaluationStatus.FAIL

    assert result.dimensions["outcome"] is EvaluationStatus.PASS


def test_dimensions_are_immutable() -> None:
    result = make_result()

    with pytest.raises(TypeError):
        result.dimensions["outcome"] = EvaluationStatus.FAIL


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(TypeError, match="reasons must be a tuple"):
        make_result(reasons=["failed"])


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="evaluation reasons must be strings",
    ):
        make_result(reasons=(123,))


def test_metadata_must_be_mapping() -> None:
    with pytest.raises(TypeError, match="metadata must be a mapping"):
        make_result(metadata=[])


def test_metadata_is_mapping_proxy() -> None:
    result = make_result()

    assert isinstance(result.metadata, MappingProxyType)


def test_metadata_is_copied() -> None:
    metadata = {"source": "test"}
    result = make_result(metadata=metadata)

    metadata["source"] = "changed"

    assert result.metadata["source"] == "test"


def test_metadata_is_immutable() -> None:
    result = make_result()

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_result_is_immutable() -> None:
    result = make_result()

    with pytest.raises(FrozenInstanceError):
        result.status = EvaluationStatus.FAIL


def test_create_factory_preserves_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    result = EvaluationResult.create(
        execution_id="execution-123",
        context_id=context_id,
        correlation_id=correlation_id,
        status=EvaluationStatus.PASS,
    )

    assert result.execution_id == "execution-123"
    assert result.context_id == context_id
    assert result.correlation_id == correlation_id


def test_create_factory_defaults_optional_mappings() -> None:
    result = EvaluationResult.create(
        execution_id="execution-123",
        context_id=uuid4(),
        correlation_id=uuid4(),
        status=EvaluationStatus.UNKNOWN,
    )

    assert result.dimensions == {}
    assert result.metadata == {}
    assert result.reasons == ()


def test_result_supports_all_statuses() -> None:
    for status in EvaluationStatus:
        result = make_result(status=status)
        assert result.status is status
