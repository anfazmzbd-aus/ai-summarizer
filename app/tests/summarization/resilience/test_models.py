"""
Tests for V9.3-M8 resilience models.
"""

from __future__ import annotations

import pytest

from app.summarization.resilience.models import (
    FallbackAction,
    FallbackDecision,
    ResilienceFailure,
)
from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


def failure(
    *,
    strategy=SummarizationStrategyType.HIERARCHICAL,
    attempt=1,
    retryable=True,
):
    return ResilienceFailure(
        error_type="RuntimeError",
        message="provider execution failed",
        strategy=strategy,
        attempt=attempt,
        retryable=retryable,
        metadata={},
    )


def decision(
    *,
    action=FallbackAction.FALLBACK,
    failed_strategy=SummarizationStrategyType.HIERARCHICAL,
    fallback_strategy=SummarizationStrategyType.MAP_REDUCE,
):
    return FallbackDecision(
        action=action,
        failed_strategy=failed_strategy,
        fallback_strategy=fallback_strategy,
        failure=failure(
            strategy=failed_strategy,
        ),
        attempted_strategies=(failed_strategy,),
        max_attempts=3,
        reason="test",
        metadata={},
    )


def test_failure_is_immutable():
    value = failure()

    with pytest.raises(AttributeError):
        value.message = "changed"


def test_failure_requires_valid_strategy():
    with pytest.raises(TypeError):
        ResilienceFailure(
            error_type="RuntimeError",
            message="failure",
            strategy="hierarchical",
            attempt=1,
        )


def test_failure_attempt_must_be_positive():
    with pytest.raises(ValueError):
        failure(attempt=0)


def test_failure_retryable_must_be_boolean():
    with pytest.raises(TypeError):
        ResilienceFailure(
            error_type="RuntimeError",
            message="failure",
            strategy=SummarizationStrategyType.DIRECT,
            attempt=1,
            retryable="yes",
        )


def test_decision_is_immutable():
    value = decision()

    with pytest.raises(AttributeError):
        value.action = FallbackAction.TERMINATE


def test_fallback_requires_target_strategy():
    with pytest.raises(ValueError):
        FallbackDecision(
            action=FallbackAction.FALLBACK,
            failed_strategy=SummarizationStrategyType.HIERARCHICAL,
            fallback_strategy=None,
            failure=failure(),
            attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
            max_attempts=3,
            reason="test",
            metadata={},
        )


def test_terminate_cannot_have_fallback_strategy():
    with pytest.raises(ValueError):
        decision(
            action=FallbackAction.TERMINATE,
        )


def test_retry_cannot_have_fallback_strategy():
    with pytest.raises(ValueError):
        decision(
            action=FallbackAction.RETRY,
        )


def test_failed_strategy_must_be_attempted():
    with pytest.raises(ValueError):
        FallbackDecision(
            action=FallbackAction.FALLBACK,
            failed_strategy=SummarizationStrategyType.DIRECT,
            fallback_strategy=SummarizationStrategyType.MAP_REDUCE,
            failure=failure(
                strategy=SummarizationStrategyType.DIRECT,
            ),
            attempted_strategies=(SummarizationStrategyType.HIERARCHICAL,),
            max_attempts=3,
            reason="test",
            metadata={},
        )
