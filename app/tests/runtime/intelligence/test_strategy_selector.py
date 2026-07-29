"""
Unit tests for V7.9 StrategySelector.
"""

from dataclasses import FrozenInstanceError

import pytest

from app.runtime.intelligence.execution_strategy import ExecutionStrategy
from app.runtime.intelligence.reasoning_result import ReasoningResult
from app.runtime.intelligence.strategy_selector import StrategySelector
from app.runtime.intelligence.strategy_types import ExecutionStrategyType


@pytest.fixture
def selector() -> StrategySelector:
    return StrategySelector()


def make_reasoning(
    *,
    workload_size: int = 0,
    estimated_parallelism: int = 1,
    cache_available: bool = False,
    cancellation_requested: bool = False,
    timeout_risk: bool = False,
    retry_pressure: bool = False,
    policy_restricted: bool = False,
) -> ReasoningResult:
    return ReasoningResult(
        workload_size=workload_size,
        estimated_parallelism=estimated_parallelism,
        cache_available=cache_available,
        cancellation_requested=cancellation_requested,
        timeout_risk=timeout_risk,
        retry_pressure=retry_pressure,
        policy_restricted=policy_restricted,
    )


def test_default_strategy_selected(selector: StrategySelector):
    reasoning = make_reasoning()

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.DEFAULT


def test_balanced_strategy_selected(selector: StrategySelector):
    reasoning = make_reasoning(
        estimated_parallelism=3,
    )

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.BALANCED


def test_conservative_strategy_selected(selector: StrategySelector):
    reasoning = make_reasoning(
        policy_restricted=True,
        estimated_parallelism=8,
    )

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.CONSERVATIVE


def test_retry_pressure_selects_recovery(selector: StrategySelector):
    reasoning = make_reasoning(
        retry_pressure=True,
    )

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.RECOVERY


def test_timeout_risk_selects_recovery(selector: StrategySelector):
    reasoning = make_reasoning(
        timeout_risk=True,
    )

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.RECOVERY


def test_cancellation_selects_recovery(selector: StrategySelector):
    reasoning = make_reasoning(
        cancellation_requested=True,
    )

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.RECOVERY


def test_precedence_cancellation_overrides_everything(
    selector: StrategySelector,
):
    reasoning = make_reasoning(
        estimated_parallelism=10,
        retry_pressure=True,
        timeout_risk=True,
        policy_restricted=True,
        cancellation_requested=True,
    )

    strategy = selector.select(reasoning)

    assert strategy.strategy == ExecutionStrategyType.RECOVERY


@pytest.mark.parametrize(
    "strategy_type,"
    "parallel_execution,"
    "use_cache,"
    "enable_retry,"
    "checkpoint_enabled,"
    "timeout_multiplier",
    [
        (
            ExecutionStrategyType.DEFAULT,
            True,
            True,
            True,
            False,
            1.0,
        ),
        (
            ExecutionStrategyType.BALANCED,
            True,
            True,
            True,
            True,
            1.0,
        ),
        (
            ExecutionStrategyType.CONSERVATIVE,
            False,
            True,
            True,
            True,
            1.25,
        ),
        (
            ExecutionStrategyType.RECOVERY,
            False,
            True,
            True,
            True,
            2.0,
        ),
    ],
)
def test_strategy_profiles(
    selector: StrategySelector,
    strategy_type,
    parallel_execution,
    use_cache,
    enable_retry,
    checkpoint_enabled,
    timeout_multiplier,
):
    strategy = selector._build_strategy(strategy_type)

    assert strategy.parallel_execution is parallel_execution
    assert strategy.use_cache is use_cache
    assert strategy.enable_retry is enable_retry
    assert strategy.checkpoint_enabled is checkpoint_enabled
    assert strategy.timeout_multiplier == timeout_multiplier


def test_strategy_selection_is_deterministic(
    selector: StrategySelector,
):
    reasoning = make_reasoning(
        estimated_parallelism=5,
    )

    strategy_one = selector.select(reasoning)
    strategy_two = selector.select(reasoning)

    assert strategy_one == strategy_two


def test_none_reasoning_raises_value_error(
    selector: StrategySelector,
):
    with pytest.raises(ValueError):
        selector.select(None)


def test_reasoning_result_not_modified(
    selector: StrategySelector,
):
    reasoning = make_reasoning(
        estimated_parallelism=4,
    )

    original = reasoning

    selector.select(reasoning)

    assert reasoning == original


def test_execution_strategy_is_immutable(
    selector: StrategySelector,
):
    strategy = selector.select(make_reasoning())

    with pytest.raises(FrozenInstanceError):
        strategy.parallel_execution = False


def test_build_strategy_returns_execution_strategy(
    selector: StrategySelector,
):
    strategy = selector.select(make_reasoning())

    assert isinstance(strategy, ExecutionStrategy)
