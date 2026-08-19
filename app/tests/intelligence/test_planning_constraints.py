"""
Complete tests for the V10 PlanningConstraints contract.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import PlanningConstraints
from app.summarization.strategies.models import SummarizationStrategyType


def test_defaults_are_empty() -> None:
    constraints = PlanningConstraints()

    assert constraints.max_input_tokens is None
    assert constraints.max_chunks is None
    assert constraints.allowed_strategies == ()
    assert constraints.required_strategy is None
    assert constraints.has_strategy_constraint is False


def test_accepts_numeric_constraints() -> None:
    constraints = PlanningConstraints(
        max_input_tokens=1000,
        max_chunks=5,
    )

    assert constraints.max_input_tokens == 1000
    assert constraints.max_chunks == 5


def test_accepts_strategy_constraints() -> None:
    constraints = PlanningConstraints(
        allowed_strategies=(
            SummarizationStrategyType.DIRECT,
            SummarizationStrategyType.MAP_REDUCE,
        ),
        required_strategy=SummarizationStrategyType.DIRECT,
    )

    assert constraints.has_strategy_constraint is True
    assert SummarizationStrategyType.DIRECT in constraints.allowed_strategies
    assert constraints.required_strategy is SummarizationStrategyType.DIRECT


def test_rejects_non_integer_max_input_tokens() -> None:
    with pytest.raises(
        TypeError,
        match="max_input_tokens must be an integer",
    ):
        PlanningConstraints(max_input_tokens="1000")  # type: ignore[arg-type]


def test_rejects_non_positive_max_input_tokens() -> None:
    with pytest.raises(
        ValueError,
        match="max_input_tokens must be greater than zero",
    ):
        PlanningConstraints(max_input_tokens=0)


def test_rejects_non_integer_max_chunks() -> None:
    with pytest.raises(
        TypeError,
        match="max_chunks must be an integer",
    ):
        PlanningConstraints(max_chunks="5")  # type: ignore[arg-type]


def test_rejects_non_positive_max_chunks() -> None:
    with pytest.raises(
        ValueError,
        match="max_chunks must be greater than zero",
    ):
        PlanningConstraints(max_chunks=0)


def test_rejects_invalid_allowed_strategy_collection() -> None:
    with pytest.raises(
        TypeError,
        match="allowed_strategies must be a tuple",
    ):
        PlanningConstraints(
            allowed_strategies=[SummarizationStrategyType.DIRECT]  # type: ignore[arg-type]
        )


def test_rejects_invalid_strategy_value() -> None:
    with pytest.raises(
        TypeError,
        match="allowed_strategies must contain only",
    ):
        PlanningConstraints(allowed_strategies=("direct",))  # type: ignore[arg-type]


def test_rejects_invalid_required_strategy() -> None:
    with pytest.raises(
        TypeError,
        match="required_strategy must be a SummarizationStrategyType",
    ):
        PlanningConstraints(required_strategy="direct")  # type: ignore[arg-type]


def test_required_strategy_must_be_allowed() -> None:
    with pytest.raises(
        ValueError,
        match="required_strategy must be included",
    ):
        PlanningConstraints(
            allowed_strategies=(SummarizationStrategyType.MAP_REDUCE,),
            required_strategy=SummarizationStrategyType.DIRECT,
        )


def test_metadata_is_immutable() -> None:
    constraints = PlanningConstraints(
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        constraints.metadata["source"] = "changed"  # type: ignore[index]


def test_contract_is_frozen() -> None:
    constraints = PlanningConstraints()

    with pytest.raises(FrozenInstanceError):
        constraints.max_chunks = 10  # type: ignore[misc]


def test_from_mapping_parses_integer_constraints() -> None:
    constraints = PlanningConstraints.from_mapping(
        {
            "max_input_tokens": 1000,
            "max_chunks": 5,
        }
    )

    assert constraints.max_input_tokens == 1000
    assert constraints.max_chunks == 5


def test_from_mapping_parses_strategy_names() -> None:
    constraints = PlanningConstraints.from_mapping(
        {
            "allowed_strategies": [
                "direct",
                "map_reduce",
            ],
            "required_strategy": "direct",
        }
    )

    assert constraints.allowed_strategies == (
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.MAP_REDUCE,
    )

    assert constraints.required_strategy is SummarizationStrategyType.DIRECT


def test_from_mapping_accepts_strategy_enums() -> None:
    constraints = PlanningConstraints.from_mapping(
        {
            "allowed_strategies": (SummarizationStrategyType.DIRECT,),
            "required_strategy": SummarizationStrategyType.DIRECT,
        }
    )

    assert constraints.allowed_strategies == (SummarizationStrategyType.DIRECT,)


def test_from_mapping_accepts_none_allowed_strategies() -> None:
    constraints = PlanningConstraints.from_mapping(
        {
            "allowed_strategies": None,
        }
    )

    assert constraints.allowed_strategies == ()


def test_from_mapping_accepts_single_strategy_string() -> None:
    constraints = PlanningConstraints.from_mapping(
        {
            "allowed_strategies": "direct",
        }
    )

    assert constraints.allowed_strategies == (SummarizationStrategyType.DIRECT,)


def test_from_mapping_rejects_unknown_strategy() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported summarization strategy",
    ):
        PlanningConstraints.from_mapping(
            {
                "allowed_strategies": ["unknown"],
            }
        )


def test_from_mapping_rejects_invalid_allowed_strategy_type() -> None:
    with pytest.raises(
        TypeError,
        match="allowed_strategies values must be strategy names",
    ):
        PlanningConstraints.from_mapping(
            {
                "allowed_strategies": [123],
            }
        )


def test_from_mapping_rejects_invalid_required_strategy_type() -> None:
    with pytest.raises(
        TypeError,
        match="required_strategy must be a strategy name",
    ):
        PlanningConstraints.from_mapping(
            {
                "required_strategy": 123,
            }
        )


def test_from_mapping_rejects_non_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="constraints must be a mapping",
    ):
        PlanningConstraints.from_mapping([])  # type: ignore[arg-type]
