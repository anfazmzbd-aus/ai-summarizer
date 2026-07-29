# import pytest
from app.runtime.intelligence.strategy_types import ExecutionStrategyType


def test_tc_st_001_default_strategy_exists():
    assert hasattr(ExecutionStrategyType, "DEFAULT")


def test_tc_st_002_all_strategy_values_unique():
    values = [strategy.value for strategy in ExecutionStrategyType]
    assert len(values) == len(set(values))


def test_tc_st_003_strategy_values_are_json_compatible():
    assert isinstance(ExecutionStrategyType.DEFAULT.value, str)


def test_tc_st_004_future_strategies_exist():
    assert hasattr(ExecutionStrategyType, "BALANCED")
    assert hasattr(ExecutionStrategyType, "CONSERVATIVE")
    assert hasattr(ExecutionStrategyType, "RECOVERY")
    assert hasattr(ExecutionStrategyType, "AGGRESSIVE")
