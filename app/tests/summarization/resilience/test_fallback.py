"""
Tests for V9.3-M8 deterministic fallback planning.
"""

from __future__ import annotations

import pytest

from app.summarization.resilience import (
    FallbackAction,
    ResilienceFailure,
    ResilienceFallbackPlanner,
)
from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


def make_failure(
    strategy: SummarizationStrategyType,
    *,
    attempt: int = 1,
    retryable: bool = True,
):
    return ResilienceFailure(
        error_type="ExecutionError",
        message="strategy execution failed",
        strategy=strategy,
        attempt=attempt,
        retryable=retryable,
    )


def test_hierarchical_falls_back_to_map_reduce():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
        ),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert decision.action is FallbackAction.FALLBACK
    assert decision.fallback_strategy is SummarizationStrategyType.MAP_REDUCE


def test_map_reduce_falls_back_to_direct():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.MAP_REDUCE,
        ),
        attempted_strategies=(SummarizationStrategyType.MAP_REDUCE,),
    )

    assert decision.action is FallbackAction.FALLBACK
    assert decision.fallback_strategy is SummarizationStrategyType.DIRECT


def test_direct_has_no_lower_fallback():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.DIRECT,
        ),
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.action is FallbackAction.RETRY
    assert decision.fallback_strategy is None


def test_direct_failure_terminates_when_retry_budget_exhausted():
    decision = ResilienceFallbackPlanner(
        max_attempts=2,
    ).decide(
        failure=make_failure(
            SummarizationStrategyType.DIRECT,
            attempt=2,
        ),
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.action is FallbackAction.TERMINATE
    assert decision.fallback_strategy is None


def test_non_retryable_failure_terminates():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.DIRECT,
            retryable=False,
        ),
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
    )

    assert decision.action is FallbackAction.TERMINATE


def test_hierarchical_skips_already_attempted_fallback():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
        ),
        attempted_strategies=(
            SummarizationStrategyType.HIERARCHICAL,
            SummarizationStrategyType.MAP_REDUCE,
        ),
    )

    assert decision.action is FallbackAction.FALLBACK
    assert decision.fallback_strategy is SummarizationStrategyType.DIRECT


def test_all_fallbacks_exhausted_then_retry_is_used():
    decision = ResilienceFallbackPlanner(
        max_attempts=3,
    ).decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
            attempt=1,
        ),
        attempted_strategies=(
            SummarizationStrategyType.HIERARCHICAL,
            SummarizationStrategyType.MAP_REDUCE,
            SummarizationStrategyType.DIRECT,
        ),
    )

    assert decision.action is FallbackAction.RETRY
    assert decision.fallback_strategy is None


def test_all_fallbacks_exhausted_and_budget_used_terminates():
    decision = ResilienceFallbackPlanner(
        max_attempts=3,
    ).decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
            attempt=3,
        ),
        attempted_strategies=(
            SummarizationStrategyType.HIERARCHICAL,
            SummarizationStrategyType.MAP_REDUCE,
            SummarizationStrategyType.DIRECT,
        ),
    )

    assert decision.action is FallbackAction.TERMINATE


def test_failure_provenance_is_preserved():
    failure = make_failure(
        SummarizationStrategyType.HIERARCHICAL,
    )

    decision = ResilienceFallbackPlanner().decide(
        failure=failure,
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert decision.failure is failure
    assert decision.failure.error_type == "ExecutionError"
    assert decision.failure.message == "strategy execution failed"


def test_attempted_strategies_are_preserved():
    attempted = (
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    )

    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.MAP_REDUCE,
        ),
        attempted_strategies=attempted,
    )

    assert decision.attempted_strategies == attempted


def test_duplicate_attempts_are_normalized():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
        ),
        attempted_strategies=(
            SummarizationStrategyType.HIERARCHICAL,
            SummarizationStrategyType.HIERARCHICAL,
        ),
    )

    assert decision.attempted_strategies == (SummarizationStrategyType.HIERARCHICAL,)


def test_failed_strategy_is_added_when_missing():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
        ),
        attempted_strategies=(),
    )

    assert decision.attempted_strategies == (SummarizationStrategyType.HIERARCHICAL,)


def test_planner_is_deterministic():
    failure = make_failure(
        SummarizationStrategyType.HIERARCHICAL,
    )

    planner = ResilienceFallbackPlanner()

    first = planner.decide(
        failure=failure,
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    second = planner.decide(
        failure=failure,
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert first == second


def test_planner_metadata_contains_version():
    decision = ResilienceFallbackPlanner().decide(
        failure=make_failure(
            SummarizationStrategyType.HIERARCHICAL,
        ),
        attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
    )

    assert decision.metadata["planner_version"] == "v9.3-m8"


def test_invalid_failure_is_rejected():
    with pytest.raises(TypeError):
        ResilienceFallbackPlanner().decide(
            failure=object(),
            attempted_strategies=(),
        )


def test_invalid_attempted_strategy_is_rejected():
    with pytest.raises(TypeError):
        ResilienceFallbackPlanner().decide(
            failure=make_failure(
                SummarizationStrategyType.DIRECT,
            ),
            attempted_strategies=("direct",),
        )


def test_string_attempted_strategies_are_rejected():
    with pytest.raises(TypeError):
        ResilienceFallbackPlanner().decide(
            failure=make_failure(
                SummarizationStrategyType.DIRECT,
            ),
            attempted_strategies="direct",
        )


def test_invalid_max_attempts_is_rejected():
    with pytest.raises(ValueError):
        ResilienceFallbackPlanner(
            max_attempts=0,
        )


def test_max_attempts_must_be_integer():
    with pytest.raises(TypeError):
        ResilienceFallbackPlanner(
            max_attempts=2.5,
        )
