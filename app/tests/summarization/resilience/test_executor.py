"""
Tests for the V9.3-M8 execution failure resilience boundary.
"""

from __future__ import annotations

import pytest

from app.summarization.resilience import (
    FallbackAction,
    ResilientExecutionPlanner,
)
from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


def test_execution_failure_creates_hierarchical_fallback():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("provider unavailable"),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert decision.action is FallbackAction.FALLBACK

    assert decision.fallback_strategy is SummarizationStrategyType.MAP_REDUCE


def test_execution_failure_creates_direct_fallback():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.MAP_REDUCE,
        exception=RuntimeError("execution failed"),
        attempted_strategies=(SummarizationStrategyType.MAP_REDUCE,),
    )

    assert decision.action is FallbackAction.FALLBACK

    assert decision.fallback_strategy is SummarizationStrategyType.DIRECT


def test_direct_execution_failure_retries_when_budget_available():
    planner = ResilientExecutionPlanner(
        max_attempts=2,
    )

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.DIRECT,
        exception=RuntimeError("execution failed"),
        attempt=1,
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.action is FallbackAction.RETRY
    assert decision.fallback_strategy is None


def test_direct_execution_failure_terminates_when_budget_exhausted():
    planner = ResilientExecutionPlanner(
        max_attempts=2,
    )

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.DIRECT,
        exception=RuntimeError("execution failed"),
        attempt=2,
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.action is FallbackAction.TERMINATE
    assert decision.fallback_strategy is None


def test_non_retryable_execution_failure_terminates():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.DIRECT,
        exception=ValueError("invalid request"),
        retryable=False,
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.action is FallbackAction.TERMINATE


def test_exception_type_is_preserved():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=TimeoutError("provider timed out"),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert decision.failure.error_type == "TimeoutError"


def test_exception_message_is_preserved():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("summarization worker failed"),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert decision.failure.message == "summarization worker failed"


def test_failure_strategy_is_preserved():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.MAP_REDUCE,
        exception=RuntimeError("failed"),
        attempted_strategies=(SummarizationStrategyType.MAP_REDUCE,),
    )

    assert decision.failure.strategy is SummarizationStrategyType.MAP_REDUCE

    assert decision.failed_strategy is SummarizationStrategyType.MAP_REDUCE


def test_attempt_is_preserved():
    planner = ResilientExecutionPlanner(
        max_attempts=3,
    )

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.DIRECT,
        exception=RuntimeError("failed"),
        attempt=2,
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.failure.attempt == 2


def test_custom_metadata_is_preserved():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("failed"),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
        metadata={
            "execution_id": "test-123",
            "node_id": "summary",
        },
    )

    assert decision.failure.metadata["execution_id"] == "test-123"

    assert decision.failure.metadata["node_id"] == "summary"

    assert decision.failure.metadata["planner_version"] == "v9.3-m8"


def test_empty_attempt_history_is_supported():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("failed"),
    )

    assert decision.attempted_strategies == (SummarizationStrategyType.HIERARCHICAL,)


def test_attempt_history_is_forwarded():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("failed"),
        attempted_strategies=(
            SummarizationStrategyType.HIERARCHICAL,
            SummarizationStrategyType.MAP_REDUCE,
        ),
    )

    assert decision.attempted_strategies == (
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    )

    assert decision.fallback_strategy is SummarizationStrategyType.DIRECT


def test_planner_is_deterministic():
    planner = ResilientExecutionPlanner()

    first = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("failed"),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    second = planner.decide_from_exception(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        exception=RuntimeError("failed"),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert first == second


def test_provider_exception_requires_no_provider_dependency():
    planner = ResilientExecutionPlanner()

    decision = planner.decide_from_exception(
        strategy=SummarizationStrategyType.DIRECT,
        exception=RuntimeError("provider failure"),
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.metadata["planner_version"] == "v9.3-m8"


def test_invalid_strategy_is_rejected():
    with pytest.raises(TypeError):
        ResilientExecutionPlanner().decide_from_exception(
            strategy="direct",
            exception=RuntimeError("failed"),
        )


def test_invalid_exception_is_rejected():
    with pytest.raises(TypeError):
        ResilientExecutionPlanner().decide_from_exception(
            strategy=SummarizationStrategyType.DIRECT,
            exception="failed",
        )


def test_invalid_attempt_is_rejected():
    with pytest.raises(ValueError):
        ResilientExecutionPlanner().decide_from_exception(
            strategy=SummarizationStrategyType.DIRECT,
            exception=RuntimeError("failed"),
            attempt=0,
        )


def test_invalid_attempt_type_is_rejected():
    with pytest.raises(TypeError):
        ResilientExecutionPlanner().decide_from_exception(
            strategy=SummarizationStrategyType.DIRECT,
            exception=RuntimeError("failed"),
            attempt=1.5,
        )


def test_invalid_retryable_value_is_rejected():
    with pytest.raises(TypeError):
        ResilientExecutionPlanner().decide_from_exception(
            strategy=SummarizationStrategyType.DIRECT,
            exception=RuntimeError("failed"),
            retryable="yes",
        )


def test_invalid_metadata_is_rejected():
    with pytest.raises(TypeError):
        ResilientExecutionPlanner().decide_from_exception(
            strategy=SummarizationStrategyType.DIRECT,
            exception=RuntimeError("failed"),
            metadata="invalid",
        )
