"""
Tests for V7.9 RuntimeReasoner.

Validates:
- Runtime observation extraction
- Safe defaults
- Deterministic reasoning
- Read-only behavior
"""

from copy import deepcopy

import pytest

from app.orchestration.execution.execution_context import ExecutionContext
from app.runtime.intelligence.runtime_reasoner import RuntimeReasoner


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
def reasoner():
    return RuntimeReasoner()


@pytest.fixture
def empty_context():
    return ExecutionContext()


def test_empty_context_returns_safe_defaults(
    reasoner,
    empty_context,
):
    result = reasoner.reason(empty_context)

    assert result.workload_size == 0
    assert result.estimated_parallelism == 1
    assert result.cache_available is False
    assert result.cancellation_requested is False
    assert result.timeout_risk is False
    assert result.retry_pressure is False
    assert result.policy_restricted is False


def test_workload_size_from_execution_graph(reasoner, empty_context):
    empty_context.execution_graph = MockExecutionGraph(
        nodes={
            "summary": {},
            "insights": {},
            "risk": {},
        }
    )

    result = reasoner.reason(empty_context)

    assert result.workload_size == 3


def test_parallelism_from_execution_layers(
    reasoner,
    empty_context,
):
    empty_context.execution_graph = MockExecutionGraph(
        layers=[
            ["summary"],
            [
                "insights",
                "sentiment",
                "findings",
            ],
            ["recommendation"],
        ]
    )

    result = reasoner.reason(empty_context)

    assert result.estimated_parallelism == 3


def test_cache_detection(reasoner, empty_context):
    empty_context.runtime_cache = MockRuntimeCache(enabled=True)

    result = reasoner.reason(empty_context)

    assert result.cache_available is True


def test_cache_disabled_returns_false(
    reasoner,
    empty_context,
):
    empty_context.runtime_cache = MockRuntimeCache(enabled=False)

    result = reasoner.reason(empty_context)

    assert result.cache_available is False


def test_cancellation_detection(
    reasoner,
    empty_context,
):
    empty_context.cancellation_token = MockCancellationToken(is_cancelled=True)

    result = reasoner.reason(empty_context)

    assert result.cancellation_requested is True


def test_timeout_risk_detection(
    reasoner,
    empty_context,
):
    empty_context.runtime_metadata = MockRuntimeMetadata(timeout_risk=True)

    result = reasoner.reason(empty_context)

    assert result.timeout_risk is True


def test_retry_pressure_detection(
    reasoner,
    empty_context,
):
    empty_context.runtime_metadata = MockRuntimeMetadata(retry_pressure=True)

    result = reasoner.reason(empty_context)

    assert result.retry_pressure is True


def test_policy_restriction_detection(
    reasoner,
    empty_context,
):
    empty_context.policy_engine = MockPolicyEngine(restricted=True)

    result = reasoner.reason(empty_context)

    assert result.policy_restricted is True


def test_missing_optional_components_do_not_fail(
    reasoner,
    empty_context,
):
    empty_context.execution_graph = None
    empty_context.runtime_cache = None
    empty_context.runtime_metadata = None
    empty_context.policy_engine = None

    result = reasoner.reason(empty_context)

    assert result is not None
    assert result.workload_size == 0


def test_context_is_not_mutated(
    reasoner,
    empty_context,
):
    empty_context.execution_graph = MockExecutionGraph(
        nodes={"summary": {}},
        layers=[["summary"]],
    )

    original = deepcopy(empty_context)

    reasoner.reason(empty_context)

    assert empty_context == original


def test_reasoning_is_deterministic(
    reasoner,
    empty_context,
):
    empty_context.execution_graph = MockExecutionGraph(
        nodes={
            "summary": {},
            "insights": {},
        },
        layers=[
            [
                "summary",
                "insights",
            ]
        ],
    )

    result_one = reasoner.reason(empty_context)
    result_two = reasoner.reason(empty_context)

    assert result_one == result_two


def test_none_context_raises_error(reasoner):
    with pytest.raises(ValueError):
        reasoner.reason(None)
