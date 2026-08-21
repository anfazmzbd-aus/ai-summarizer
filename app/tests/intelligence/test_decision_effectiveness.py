"""Tests for the V10 decision effectiveness contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType
from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionEffectiveness,
    EffectivenessDimension,
    EffectivenessStatus,
)


def make_effectiveness(
    *,
    status: EffectivenessStatus = EffectivenessStatus.EFFECTIVE,
    dimensions=None,
    reasons: tuple[str, ...] = (),
    metadata=None,
) -> DecisionEffectiveness:
    return DecisionEffectiveness.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        status=status,
        dimensions={} if dimensions is None else dimensions,
        reasons=reasons,
        metadata={} if metadata is None else metadata,
    )


def test_effectiveness_status_values_are_stable() -> None:
    assert EffectivenessStatus.EFFECTIVE.value == "effective"
    assert EffectivenessStatus.DEGRADED.value == "degraded"
    assert EffectivenessStatus.INEFFECTIVE.value == "ineffective"
    assert EffectivenessStatus.UNKNOWN.value == "unknown"


def test_effectiveness_dimension_values_are_stable() -> None:
    assert EffectivenessDimension.OUTCOME.value == "outcome"
    assert EffectivenessDimension.QUALITY.value == "quality"
    assert EffectivenessDimension.PERFORMANCE.value == "performance"
    assert EffectivenessDimension.RELIABILITY.value == "reliability"


def test_valid_effectiveness_contract() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    result = DecisionEffectiveness.create(
        context_id=context_id,
        correlation_id=correlation_id,
        execution_id="execution-001",
        status=EffectivenessStatus.EFFECTIVE,
        dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        },
        reasons=("execution succeeded",),
        metadata={"source": "test"},
    )

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id
    assert result.execution_id == "execution-001"
    assert result.status is EffectivenessStatus.EFFECTIVE
    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.EFFECTIVE
    )
    assert result.reasons == ("execution succeeded",)
    assert result.metadata["source"] == "test"


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        DecisionEffectiveness.create(
            context_id="invalid",
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id="invalid",
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
        )


def test_execution_id_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="execution_id must be a string",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id=123,
            status=EffectivenessStatus.EFFECTIVE,
        )


def test_execution_id_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="execution_id must not be empty",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="",
            status=EffectivenessStatus.EFFECTIVE,
        )


def test_status_must_be_effectiveness_status() -> None:
    with pytest.raises(
        TypeError,
        match="status must be an EffectivenessStatus",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status="effective",
        )


def test_dimensions_must_be_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="dimensions must be a mapping",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
            dimensions=[],
        )


def test_dimension_keys_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("dimension keys must be " "EffectivenessDimension values"),
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
            dimensions={
                "outcome": EffectivenessStatus.EFFECTIVE,
            },
        )


def test_dimension_values_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("dimension values must be " "EffectivenessStatus values"),
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
            dimensions={
                EffectivenessDimension.OUTCOME: "effective",
            },
        )


def test_all_dimensions_are_supported() -> None:
    result = make_effectiveness(
        dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            EffectivenessDimension.QUALITY: EffectivenessStatus.UNKNOWN,
            EffectivenessDimension.PERFORMANCE: EffectivenessStatus.DEGRADED,
            EffectivenessDimension.RELIABILITY: EffectivenessStatus.EFFECTIVE,
        }
    )

    assert set(result.dimensions) == {
        EffectivenessDimension.OUTCOME,
        EffectivenessDimension.QUALITY,
        EffectivenessDimension.PERFORMANCE,
        EffectivenessDimension.RELIABILITY,
    }


def test_dimensions_are_mapping_proxy() -> None:
    result = make_effectiveness(
        dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        }
    )

    assert isinstance(result.dimensions, MappingProxyType)


def test_dimensions_are_immutable() -> None:
    result = make_effectiveness(
        dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        }
    )

    with pytest.raises(TypeError):
        result.dimensions[EffectivenessDimension.OUTCOME] = EffectivenessStatus.DEGRADED


def test_dimensions_are_defensively_copied() -> None:
    dimensions = {
        EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
    }

    result = make_effectiveness(dimensions=dimensions)

    dimensions[EffectivenessDimension.OUTCOME] = EffectivenessStatus.INEFFECTIVE

    assert (
        result.dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.EFFECTIVE
    )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
            reasons=(123,),
        )


def test_reasons_preserve_order() -> None:
    result = make_effectiveness(
        reasons=(
            "first",
            "second",
            "third",
        )
    )

    assert result.reasons == (
        "first",
        "second",
        "third",
    )


def test_metadata_must_be_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="metadata must be a mapping",
    ):
        DecisionEffectiveness.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            status=EffectivenessStatus.EFFECTIVE,
            metadata=[],
        )


def test_metadata_is_mapping_proxy() -> None:
    result = make_effectiveness(
        metadata={"source": "test"},
    )

    assert isinstance(result.metadata, MappingProxyType)


def test_metadata_is_immutable() -> None:
    result = make_effectiveness(
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_metadata_is_defensively_copied() -> None:
    metadata = {"source": "original"}

    result = make_effectiveness(metadata=metadata)

    metadata["source"] = "changed"

    assert result.metadata["source"] == "original"


def test_contract_is_frozen() -> None:
    result = make_effectiveness()

    with pytest.raises(FrozenInstanceError):
        result.status = EffectivenessStatus.DEGRADED


def test_factory_defaults_dimensions_to_empty_mapping() -> None:
    result = DecisionEffectiveness.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        status=EffectivenessStatus.UNKNOWN,
    )

    assert result.dimensions == {}


def test_factory_defaults_reasons_to_empty_tuple() -> None:
    result = DecisionEffectiveness.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        status=EffectivenessStatus.UNKNOWN,
    )

    assert result.reasons == ()


def test_factory_defaults_metadata_to_empty_mapping() -> None:
    result = DecisionEffectiveness.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        status=EffectivenessStatus.UNKNOWN,
    )

    assert result.metadata == {}


@pytest.mark.parametrize(
    "status",
    list(EffectivenessStatus),
)
def test_all_effectiveness_statuses_are_supported(
    status: EffectivenessStatus,
) -> None:
    result = make_effectiveness(status=status)

    assert result.status is status


def test_contract_preserves_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    result = DecisionEffectiveness.create(
        context_id=context_id,
        correlation_id=correlation_id,
        execution_id="execution-987",
        status=EffectivenessStatus.EFFECTIVE,
    )

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id
    assert result.execution_id == "execution-987"


def test_contract_contains_no_runtime_action_fields() -> None:
    forbidden_fields = {
        "retry",
        "replan",
        "provider",
        "strategy",
        "timeout",
        "executor",
        "runtime",
        "callback",
        "reward",
        "penalty",
    }

    assert not (forbidden_fields & set(DecisionEffectiveness.__dataclass_fields__))


def test_contract_has_no_execution_methods() -> None:
    forbidden_methods = {
        "execute",
        "retry",
        "replan",
        "switch_provider",
        "select_strategy",
    }

    public_names = {
        name for name in dir(DecisionEffectiveness) if not name.startswith("_")
    }

    assert not (forbidden_methods & public_names)
