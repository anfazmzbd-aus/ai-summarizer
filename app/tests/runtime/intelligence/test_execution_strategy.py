import pytest
from dataclasses import FrozenInstanceError
from app.runtime.intelligence.strategy_types import ExecutionStrategyType
from app.runtime.intelligence.execution_strategy import ExecutionStrategy


def test_tc_es_001_strategy_creation_succeeds():
    strategy = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    assert strategy is not None
    assert strategy.strategy == ExecutionStrategyType.DEFAULT


def test_tc_es_002_strategy_is_immutable():
    strategy = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    with pytest.raises(FrozenInstanceError):
        strategy.strategy = ExecutionStrategyType.BALANCED


def test_tc_es_003_equality_works():
    strategy1 = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    strategy2 = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    assert strategy1 == strategy2


def test_tc_es_004_different_strategies_not_equal():
    strategy1 = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    strategy2 = ExecutionStrategy(
        strategy=ExecutionStrategyType.BALANCED,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    assert strategy1 != strategy2


def test_tc_es_005_hashing_works():
    strategy = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    strategy_set = {strategy}
    assert strategy in strategy_set
