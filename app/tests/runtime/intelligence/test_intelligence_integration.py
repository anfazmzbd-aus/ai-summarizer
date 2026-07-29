"""
Integration tests for the V7.9 Adaptive Runtime Intelligence pipeline.

Pipeline:

ExecutionContext
        │
        ▼
RuntimeReasoner
        │
        ▼
ReasoningResult
        │
        ▼
StrategySelector
        │
        ▼
ExecutionStrategy
        │
        ▼
DecisionEngine
        │
        ▼
Decision
"""

from dataclasses import FrozenInstanceError

import pytest

from app.orchestration.execution.execution_context import ExecutionContext
from app.runtime.intelligence.decision import Decision
from app.runtime.intelligence.decision_engine import DecisionEngine
from app.runtime.intelligence.strategy_types import ExecutionStrategyType


class MockExecutionGraph:
    def __init__(self, nodes=None, layers=None):
        self.nodes = nodes or {}
        self.layers = layers or []


class MockRuntimeCache:
    def __init__(self, enabled=True):
        self.enabled = enabled


class MockCancellationToken:
    def __init__(self, is_cancelled=False):
        self.is_cancelled = is_cancelled


class MockRuntimeMetadata:
    def __init__(
        self,
        timeout_risk=False,
        retry_pressure=False,
    ):
        self.timeout_risk = timeout_risk
        self.retry_pressure = retry_pressure


class MockPolicyEngine:
    def __init__(self, restricted=False):
        self.restricted = restricted


@pytest.fixture
def engine():
    return DecisionEngine()


@pytest.fixture
def context():
    return ExecutionContext()


def test_pipeline_returns_decision(engine, context):
    decision = engine.decide(context)

    assert isinstance(decision, Decision)


def test_default_pipeline_strategy(engine, context):
    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.DEFAULT


def test_parallel_workload_selects_balanced(engine, context):
    context.execution_graph = MockExecutionGraph(
        nodes={
            "summary": {},
            "insights": {},
            "risk": {},
        },
        layers=[
            ["summary"],
            ["insights", "risk"],
        ],
    )

    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.BALANCED


def test_policy_restriction_selects_conservative(
    engine,
    context,
):
    context.policy_engine = MockPolicyEngine(
        restricted=True,
    )

    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.CONSERVATIVE


def test_retry_pressure_selects_recovery(
    engine,
    context,
):
    context.runtime_metadata = MockRuntimeMetadata(
        retry_pressure=True,
    )

    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.RECOVERY


def test_timeout_risk_selects_recovery(
    engine,
    context,
):
    context.runtime_metadata = MockRuntimeMetadata(
        timeout_risk=True,
    )

    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.RECOVERY


def test_cancellation_has_highest_priority(
    engine,
    context,
):
    context.execution_graph = MockExecutionGraph(
        nodes={
            "a": {},
            "b": {},
        },
        layers=[
            ["a", "b"],
        ],
    )

    context.runtime_metadata = MockRuntimeMetadata(
        timeout_risk=True,
        retry_pressure=True,
    )

    context.policy_engine = MockPolicyEngine(
        restricted=True,
    )

    context.cancellation_token = MockCancellationToken(
        is_cancelled=True,
    )

    decision = engine.decide(context)

    assert decision.strategy.strategy == ExecutionStrategyType.RECOVERY


def test_reasoning_is_propagated(
    engine,
    context,
):
    context.execution_graph = MockExecutionGraph(
        nodes={
            "summary": {},
            "trend": {},
        },
        layers=[
            ["summary", "trend"],
        ],
    )

    decision = engine.decide(context)

    assert decision.reasoning.workload_size == 2
    assert decision.reasoning.estimated_parallelism == 2


def test_pipeline_is_deterministic(
    engine,
    context,
):
    decision1 = engine.decide(context)
    decision2 = engine.decide(context)

    assert decision1 == decision2


def test_decision_is_immutable(
    engine,
    context,
):
    decision = engine.decide(context)

    with pytest.raises(FrozenInstanceError):
        decision.strategy = None


def test_none_context_raises():
    engine = DecisionEngine()

    with pytest.raises(ValueError):
        engine.decide(None)
