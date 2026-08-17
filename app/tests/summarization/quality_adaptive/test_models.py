"""
Tests for V9.3-M7 adaptive execution models.
"""

from __future__ import annotations

import pytest

from app.summarization.quality import (
    SummarizationQualityEvaluator,
)
from app.summarization.quality_adaptive.models import (
    AdaptiveExecutionAction,
    AdaptiveExecutionDecision,
)
from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


def quality(
    *,
    passed: bool = True,
    score: float = 0.8,
):
    return SummarizationQualityEvaluator(
        threshold=0.60,
    ).evaluate(
        "The source contains useful information.",
        ("The source contains useful information." if passed else "unrelated"),
    )


def decision(
    *,
    action=AdaptiveExecutionAction.ACCEPT,
    current_strategy=SummarizationStrategyType.DIRECT,
    next_strategy=None,
):
    return AdaptiveExecutionDecision(
        action=action,
        current_strategy=current_strategy,
        next_strategy=next_strategy,
        quality=quality(),
        attempt=1,
        max_attempts=2,
        reason="test",
        metadata={},
    )


def test_decision_is_immutable():
    value = decision()

    with pytest.raises(AttributeError):
        value.action = AdaptiveExecutionAction.FALLBACK


def test_accept_does_not_have_next_strategy():
    with pytest.raises(ValueError):
        decision(
            action=AdaptiveExecutionAction.ACCEPT,
            next_strategy=SummarizationStrategyType.MAP_REDUCE,
        )


def test_escalation_requires_next_strategy():
    with pytest.raises(ValueError):
        decision(
            action=AdaptiveExecutionAction.ESCALATE_STRATEGY,
        )


def test_fallback_does_not_have_next_strategy():
    with pytest.raises(ValueError):
        decision(
            action=AdaptiveExecutionAction.FALLBACK,
            next_strategy=SummarizationStrategyType.MAP_REDUCE,
        )


@pytest.mark.parametrize(
    "attempt",
    [0, -1],
)
def test_attempt_must_be_positive(attempt):
    with pytest.raises(ValueError):
        AdaptiveExecutionDecision(
            action=AdaptiveExecutionAction.ACCEPT,
            current_strategy=SummarizationStrategyType.DIRECT,
            next_strategy=None,
            quality=quality(),
            attempt=attempt,
            max_attempts=2,
            reason="test",
            metadata={},
        )


def test_attempt_cannot_exceed_max_attempts():
    with pytest.raises(ValueError):
        AdaptiveExecutionDecision(
            action=AdaptiveExecutionAction.ACCEPT,
            current_strategy=SummarizationStrategyType.DIRECT,
            next_strategy=None,
            quality=quality(),
            attempt=3,
            max_attempts=2,
            reason="test",
            metadata={},
        )


def test_invalid_action_is_rejected():
    with pytest.raises(TypeError):
        AdaptiveExecutionDecision(
            action="accept",
            current_strategy=SummarizationStrategyType.DIRECT,
            next_strategy=None,
            quality=quality(),
            attempt=1,
            max_attempts=2,
            reason="test",
            metadata={},
        )
