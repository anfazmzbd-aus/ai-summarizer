"""
Complete V9.3-M5 resource optimization tests.
"""

from __future__ import annotations

import pytest

from app.summarization.planning.optimization import (
    StrategyResourceOptimizer,
)
from app.summarization.strategies.models import (
    StrategySelection,
    SummarizationStrategyType,
)


def selection(
    strategy,
    *,
    token_count=1000,
    chunk_count=2,
):
    return StrategySelection(
        strategy=strategy,
        token_count=token_count,
        chunk_count=chunk_count,
        reason="baseline",
        metadata={},
    )


@pytest.mark.parametrize(
    "strategy",
    list(SummarizationStrategyType),
)
def test_estimate_is_deterministic(strategy):
    optimizer = StrategyResourceOptimizer()

    first = optimizer.estimate(
        strategy,
        input_tokens=1200,
        chunk_count=3,
    )

    second = optimizer.estimate(
        strategy,
        input_tokens=1200,
        chunk_count=3,
    )

    assert first == second


def test_estimate_preserves_input_and_calculates_output():
    result = StrategyResourceOptimizer().estimate(
        SummarizationStrategyType.DIRECT,
        input_tokens=1000,
        chunk_count=1,
    )

    assert result.estimated_input_tokens == 1000
    assert result.estimated_output_tokens == 250
    assert result.estimated_total_tokens == 1250


def test_multi_stage_strategies_have_higher_relative_resource_cost():
    optimizer = StrategyResourceOptimizer()

    direct = optimizer.estimate(
        SummarizationStrategyType.DIRECT,
        input_tokens=2000,
        chunk_count=4,
    )

    map_reduce = optimizer.estimate(
        SummarizationStrategyType.MAP_REDUCE,
        input_tokens=2000,
        chunk_count=4,
    )

    hierarchical = optimizer.estimate(
        SummarizationStrategyType.HIERARCHICAL,
        input_tokens=2000,
        chunk_count=4,
    )

    assert direct.estimated_cost_units < map_reduce.estimated_cost_units

    assert map_reduce.estimated_cost_units < hierarchical.estimated_cost_units

    assert direct.estimated_latency_ms < map_reduce.estimated_latency_ms

    assert map_reduce.estimated_latency_ms < hierarchical.estimated_latency_ms


def test_baseline_is_retained_without_constraints():
    decision = StrategyResourceOptimizer().decide(
        selection(SummarizationStrategyType.MAP_REDUCE)
    )

    assert decision.selected_strategy is SummarizationStrategyType.MAP_REDUCE

    assert decision.constrained is False


def test_baseline_is_retained_when_constraints_are_met():
    optimizer = StrategyResourceOptimizer()

    estimate = optimizer.estimate(
        SummarizationStrategyType.DIRECT,
        input_tokens=1000,
        chunk_count=1,
    )

    decision = optimizer.decide(
        selection(
            SummarizationStrategyType.DIRECT,
            token_count=1000,
            chunk_count=1,
        ),
        max_cost_units=estimate.estimated_cost_units,
        max_latency_ms=estimate.estimated_latency_ms,
        max_total_tokens=estimate.estimated_total_tokens,
    )

    assert decision.selected_strategy is SummarizationStrategyType.DIRECT


def test_constraint_optimization_does_not_downgrade_baseline():
    decision = StrategyResourceOptimizer().decide(
        selection(
            SummarizationStrategyType.MAP_REDUCE,
            token_count=1000,
        ),
        max_cost_units=1,
    )

    assert decision.selected_strategy is SummarizationStrategyType.MAP_REDUCE


def test_no_feasible_candidate_retains_baseline():
    decision = StrategyResourceOptimizer().decide(
        selection(
            SummarizationStrategyType.DIRECT,
            token_count=5000,
        ),
        max_total_tokens=1,
    )

    assert decision.selected_strategy is SummarizationStrategyType.DIRECT

    assert decision.metadata["constraint_fallback"] is True


def test_constraints_are_recorded():
    decision = StrategyResourceOptimizer().decide(
        selection(SummarizationStrategyType.DIRECT),
        max_cost_units=20,
        max_latency_ms=1000,
        max_total_tokens=2000,
    )

    assert decision.metadata["max_cost_units"] == 20

    assert decision.metadata["max_latency_ms"] == 1000

    assert decision.metadata["max_total_tokens"] == 2000


def test_estimate_is_immutable():
    estimate = StrategyResourceOptimizer().estimate(
        SummarizationStrategyType.DIRECT,
        input_tokens=100,
        chunk_count=1,
    )

    with pytest.raises(AttributeError):
        estimate.estimated_cost_units = 99


@pytest.mark.parametrize(
    ("strategy", "input_tokens", "chunk_count"),
    [
        (
            SummarizationStrategyType.DIRECT,
            -1,
            1,
        ),
        (
            SummarizationStrategyType.DIRECT,
            1,
            -1,
        ),
    ],
)
def test_estimate_rejects_negative_metrics(
    strategy,
    input_tokens,
    chunk_count,
):
    with pytest.raises(ValueError):
        StrategyResourceOptimizer().estimate(
            strategy,
            input_tokens=input_tokens,
            chunk_count=chunk_count,
        )


def test_decide_rejects_invalid_selection():
    with pytest.raises(
        TypeError,
        match="selection",
    ):
        StrategyResourceOptimizer().decide(object())


@pytest.mark.parametrize(
    "name",
    [
        "max_cost_units",
        "max_latency_ms",
        "max_total_tokens",
    ],
)
def test_decide_rejects_negative_limits(name):
    kwargs = {name: -1}

    with pytest.raises(ValueError):
        StrategyResourceOptimizer().decide(
            selection(SummarizationStrategyType.DIRECT),
            **kwargs,
        )
