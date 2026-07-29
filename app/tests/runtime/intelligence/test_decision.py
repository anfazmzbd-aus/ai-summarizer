import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from app.runtime.intelligence.strategy_types import ExecutionStrategyType
from app.runtime.intelligence.execution_strategy import ExecutionStrategy
from app.runtime.intelligence.reasoning_result import ReasoningResult
from app.runtime.intelligence.decision import Decision


@pytest.fixture
def mock_dependencies():
    strategy = ExecutionStrategy(
        strategy=ExecutionStrategyType.DEFAULT,
        parallel_execution=True,
        use_cache=True,
        enable_retry=True,
        checkpoint_enabled=True,
        timeout_multiplier=1.0,
    )
    reasoning = ReasoningResult(
        workload_size=1,
        estimated_parallelism=3,
        cache_available=True,
        cancellation_requested=False,
        timeout_risk=False,
        retry_pressure=False,
        policy_restricted=False,
    )
    return strategy, reasoning


def test_tc_d_001_decision_creation(mock_dependencies):
    strategy, reasoning = mock_dependencies
    decision = Decision(
        strategy=strategy, reasoning=reasoning, created_at=datetime.now(timezone.utc)
    )
    assert decision is not None


def test_tc_d_002_decision_contains_strategy(mock_dependencies):
    strategy, reasoning = mock_dependencies
    decision = Decision(
        strategy=strategy, reasoning=reasoning, created_at=datetime.now(timezone.utc)
    )
    assert decision.strategy == strategy


def test_tc_d_003_decision_contains_reasoning(mock_dependencies):
    strategy, reasoning = mock_dependencies
    decision = Decision(
        strategy=strategy, reasoning=reasoning, created_at=datetime.now(timezone.utc)
    )
    assert decision.reasoning == reasoning


def test_tc_d_004_decision_immutable(mock_dependencies):
    strategy, reasoning = mock_dependencies
    decision = Decision(
        strategy=strategy, reasoning=reasoning, created_at=datetime.now(timezone.utc)
    )
    with pytest.raises(FrozenInstanceError):
        decision.created_at = datetime.now(timezone.utc)
