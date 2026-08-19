"""
Complete tests for the V10 StrategyHandoffPolicy contract.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import StrategyHandoffPolicy
from app.summarization.strategies.models import SummarizationStrategyType


def test_default_policy_is_empty() -> None:
    policy = StrategyHandoffPolicy()

    assert policy.preferred_strategy is None
    assert policy.allowed_strategies == ()
    assert policy.required_strategy is None
    assert policy.is_advisory_only is False
    assert policy.has_hard_constraint is False


def test_preferred_strategy_is_advisory() -> None:
    policy = StrategyHandoffPolicy(
        preferred_strategy=SummarizationStrategyType.MAP_REDUCE,
    )

    assert policy.preferred_strategy is SummarizationStrategyType.MAP_REDUCE
    assert policy.is_advisory_only is True
    assert policy.has_hard_constraint is False


def test_allowed_strategies_are_hard_constraints() -> None:
    policy = StrategyHandoffPolicy(
        allowed_strategies=(
            SummarizationStrategyType.DIRECT,
            SummarizationStrategyType.MAP_REDUCE,
        ),
    )

    assert policy.has_hard_constraint is True
    assert policy.is_advisory_only is False


def test_required_strategy_is_hard_constraint() -> None:
    policy = StrategyHandoffPolicy(
        required_strategy=SummarizationStrategyType.MAP_REDUCE,
    )

    assert policy.has_hard_constraint is True


def test_required_strategy_must_be_allowed() -> None:
    with pytest.raises(
        ValueError,
        match="required_strategy must be included",
    ):
        StrategyHandoffPolicy(
            allowed_strategies=(SummarizationStrategyType.DIRECT,),
            required_strategy=SummarizationStrategyType.MAP_REDUCE,
        )


def test_rejects_invalid_preferred_strategy() -> None:
    with pytest.raises(
        TypeError,
        match="preferred_strategy must be a SummarizationStrategyType",
    ):
        StrategyHandoffPolicy(
            preferred_strategy="direct",  # type: ignore[arg-type]
        )


def test_rejects_invalid_allowed_strategies() -> None:
    with pytest.raises(
        TypeError,
        match="allowed_strategies must be a tuple",
    ):
        StrategyHandoffPolicy(
            allowed_strategies=["direct"],  # type: ignore[arg-type]
        )


def test_rejects_invalid_allowed_strategy_value() -> None:
    with pytest.raises(
        TypeError,
        match="allowed_strategies must contain only",
    ):
        StrategyHandoffPolicy(
            allowed_strategies=("direct",),  # type: ignore[arg-type]
        )


def test_rejects_invalid_required_strategy() -> None:
    with pytest.raises(
        TypeError,
        match="required_strategy must be a SummarizationStrategyType",
    ):
        StrategyHandoffPolicy(
            required_strategy="direct",  # type: ignore[arg-type]
        )


def test_policy_is_frozen() -> None:
    policy = StrategyHandoffPolicy()

    with pytest.raises(FrozenInstanceError):
        policy.preferred_strategy = SummarizationStrategyType.DIRECT  # type: ignore[misc]


def test_metadata_is_immutable() -> None:
    policy = StrategyHandoffPolicy(
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        policy.metadata["source"] = "changed"  # type: ignore[index]


def test_from_mapping_parses_preference() -> None:
    policy = StrategyHandoffPolicy.from_mapping(
        {
            "preferred_strategy": "map_reduce",
        }
    )

    assert policy.preferred_strategy is SummarizationStrategyType.MAP_REDUCE
    assert policy.is_advisory_only is True


def test_from_mapping_parses_allowed_strategies() -> None:
    policy = StrategyHandoffPolicy.from_mapping(
        {
            "allowed_strategies": [
                "direct",
                "map_reduce",
            ],
        }
    )

    assert policy.allowed_strategies == (
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.MAP_REDUCE,
    )


def test_from_mapping_parses_required_strategy() -> None:
    policy = StrategyHandoffPolicy.from_mapping(
        {
            "required_strategy": "hierarchical",
        }
    )

    assert policy.required_strategy is SummarizationStrategyType.HIERARCHICAL


def test_from_mapping_parses_complete_policy() -> None:
    policy = StrategyHandoffPolicy.from_mapping(
        {
            "preferred_strategy": "map_reduce",
            "allowed_strategies": [
                "map_reduce",
                "hierarchical",
            ],
            "required_strategy": "map_reduce",
        }
    )

    assert policy.preferred_strategy is SummarizationStrategyType.MAP_REDUCE
    assert policy.allowed_strategies == (
        SummarizationStrategyType.MAP_REDUCE,
        SummarizationStrategyType.HIERARCHICAL,
    )
    assert policy.required_strategy is SummarizationStrategyType.MAP_REDUCE


def test_from_mapping_accepts_none_preference() -> None:
    policy = StrategyHandoffPolicy.from_mapping(
        {
            "preferred_strategy": None,
        }
    )

    assert policy.preferred_strategy is None


def test_from_mapping_accepts_single_allowed_strategy() -> None:
    policy = StrategyHandoffPolicy.from_mapping(
        {
            "allowed_strategies": "direct",
        }
    )

    assert policy.allowed_strategies == (SummarizationStrategyType.DIRECT,)


def test_from_mapping_rejects_unknown_preference() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported summarization strategy",
    ):
        StrategyHandoffPolicy.from_mapping(
            {
                "preferred_strategy": "unknown",
            }
        )


def test_from_mapping_rejects_unknown_required_strategy() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported summarization strategy",
    ):
        StrategyHandoffPolicy.from_mapping(
            {
                "required_strategy": "unknown",
            }
        )


def test_from_mapping_rejects_unknown_allowed_strategy() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported summarization strategy",
    ):
        StrategyHandoffPolicy.from_mapping(
            {
                "allowed_strategies": ["unknown"],
            }
        )


def test_from_mapping_rejects_non_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="strategy policy values must be a mapping",
    ):
        StrategyHandoffPolicy.from_mapping([])  # type: ignore[arg-type]
