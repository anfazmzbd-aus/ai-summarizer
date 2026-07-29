"""
Unit tests for V7.9 DecisionEngine.
"""

from dataclasses import FrozenInstanceError

import pytest

from app.orchestration.execution.execution_context import ExecutionContext
from app.runtime.intelligence.decision import Decision
from app.runtime.intelligence.decision_engine import DecisionEngine
from app.runtime.intelligence.execution_strategy import ExecutionStrategy
from app.runtime.intelligence.reasoning_result import ReasoningResult
from app.runtime.intelligence.runtime_reasoner import RuntimeReasoner
from app.runtime.intelligence.strategy_selector import StrategySelector
from app.runtime.intelligence.strategy_types import ExecutionStrategyType


class StubReasoner(RuntimeReasoner):
    def __init__(self):
        self.called = False

    def reason(self, context):
        self.called = True
        return ReasoningResult(
            workload_size=3,
            estimated_parallelism=2,
            cache_available=True,
            cancellation_requested=False,
            timeout_risk=False,
            retry_pressure=False,
            policy_restricted=False,
        )


class StubSelector(StrategySelector):
    def __init__(self):
        self.called = False

    def select(self, reasoning):
        self.called = True

        return ExecutionStrategy(
            strategy=ExecutionStrategyType.BALANCED,
            parallel_execution=True,
            use_cache=True,
            enable_retry=True,
            checkpoint_enabled=True,
            timeout_multiplier=1.0,
        )


@pytest.fixture
def context():
    return ExecutionContext()


@pytest.fixture
def reasoner():
    return StubReasoner()


@pytest.fixture
def selector():
    return StubSelector()


@pytest.fixture
def engine(reasoner, selector):
    return DecisionEngine(
        runtime_reasoner=reasoner,
        strategy_selector=selector,
    )


def test_returns_decision(engine, context):
    decision = engine.decide(context)

    assert isinstance(decision, Decision)


def test_reasoner_is_called(
    engine,
    reasoner,
    context,
):
    engine.decide(context)

    assert reasoner.called is True


def test_selector_is_called(
    engine,
    selector,
    context,
):
    engine.decide(context)

    assert selector.called is True


def test_reasoning_propagated(
    engine,
    context,
):
    decision = engine.decide(context)

    assert decision.reasoning.workload_size == 3
    assert decision.reasoning.estimated_parallelism == 2


def test_strategy_propagated(
    engine,
    context,
):
    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.BALANCED


def test_none_context_raises():
    engine = DecisionEngine()

    with pytest.raises(ValueError):
        engine.decide(None)


def test_decision_is_immutable(
    engine,
    context,
):
    decision = engine.decide(context)

    with pytest.raises(FrozenInstanceError):
        decision.strategy = None


def test_decision_is_deterministic(
    engine,
    context,
):
    decision1 = engine.decide(context)
    decision2 = engine.decide(context)

    assert decision1 == decision2


def test_default_dependencies():
    engine = DecisionEngine()

    assert isinstance(
        engine._runtime_reasoner,
        RuntimeReasoner,
    )

    assert isinstance(
        engine._strategy_selector,
        StrategySelector,
    )


def test_build_decision_returns_decision(
    engine,
    context,
):
    decision = engine.decide(context)

    assert isinstance(decision, Decision)
