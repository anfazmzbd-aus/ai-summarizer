"""
Tests for V9.3-M7 quality-aware adaptive execution.
"""

from __future__ import annotations

import pytest

from app.summarization.quality import (
    SummarizationQualityEvaluator,
)
from app.summarization.quality.models import (
    QualityEvaluation,
    QualityMetric,
    QualityMetricName,
)
from app.summarization.quality_adaptive import (
    AdaptiveExecutionAction,
    QualityAwareAdaptiveExecutor,
)
from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


def evaluator_result():
    return SummarizationQualityEvaluator().evaluate(
        "The system processes customer requests through automated summarization.",
        "The system processes customer requests through summarization.",
    )


def failed_quality(
    *,
    score: float = 0.20,
) -> QualityEvaluation:
    metrics = (
        QualityMetric(
            name=QualityMetricName.NON_EMPTY,
            score=score,
            rationale="test quality failure",
            metadata={},
        ),
    )

    return QualityEvaluation(
        score=score,
        passed=False,
        metrics=metrics,
        source_length=100,
        summary_length=20,
        evaluator_version="v9.3-m6",
        threshold=0.60,
        metadata={
            "deterministic": True,
            "test_fixture": True,
        },
    )


def test_passing_quality_is_accepted():
    result = evaluator_result()

    assert result.passed is True

    decision = QualityAwareAdaptiveExecutor().decide(
        current_strategy=SummarizationStrategyType.DIRECT,
        quality=result,
    )

    assert decision.action is AdaptiveExecutionAction.ACCEPT
    assert decision.next_strategy is None


def test_failed_direct_strategy_escalates():
    decision = QualityAwareAdaptiveExecutor().decide(
        current_strategy=SummarizationStrategyType.DIRECT,
        quality=failed_quality(),
    )

    assert decision.action is AdaptiveExecutionAction.ESCALATE_STRATEGY

    assert decision.next_strategy is SummarizationStrategyType.MAP_REDUCE


def test_failed_map_reduce_strategy_escalates():
    decision = QualityAwareAdaptiveExecutor().decide(
        current_strategy=SummarizationStrategyType.MAP_REDUCE,
        quality=failed_quality(),
    )

    assert decision.action is AdaptiveExecutionAction.ESCALATE_STRATEGY

    assert decision.next_strategy is SummarizationStrategyType.HIERARCHICAL


def test_failed_hierarchical_strategy_can_retry():
    decision = QualityAwareAdaptiveExecutor(
        max_attempts=2,
        retry_threshold=0.45,
    ).decide(
        current_strategy=SummarizationStrategyType.HIERARCHICAL,
        quality=failed_quality(score=0.20),
        attempt=1,
    )

    assert decision.action is AdaptiveExecutionAction.RETRY_CURRENT

    assert decision.next_strategy is None


def test_exhausted_hierarchical_strategy_falls_back():
    decision = QualityAwareAdaptiveExecutor(
        max_attempts=2,
        retry_threshold=0.45,
    ).decide(
        current_strategy=SummarizationStrategyType.HIERARCHICAL,
        quality=failed_quality(score=0.20),
        attempt=2,
    )

    assert decision.action is AdaptiveExecutionAction.FALLBACK

    assert decision.next_strategy is None


def test_passing_quality_always_stops_adaptation():
    result = evaluator_result()

    for strategy in SummarizationStrategyType:
        decision = QualityAwareAdaptiveExecutor().decide(
            current_strategy=strategy,
            quality=result,
        )

        assert decision.action is AdaptiveExecutionAction.ACCEPT

        assert decision.next_strategy is None


def test_strategy_progression_is_monotonic():
    executor = QualityAwareAdaptiveExecutor()
    failed = failed_quality()

    direct = executor.decide(
        current_strategy=SummarizationStrategyType.DIRECT,
        quality=failed,
    )

    assert direct.next_strategy is SummarizationStrategyType.MAP_REDUCE

    map_reduce = executor.decide(
        current_strategy=direct.next_strategy,
        quality=failed,
    )

    assert map_reduce.next_strategy is SummarizationStrategyType.HIERARCHICAL


def test_adaptive_decision_contains_quality_provenance():
    result = failed_quality()

    decision = QualityAwareAdaptiveExecutor().decide(
        current_strategy=SummarizationStrategyType.DIRECT,
        quality=result,
    )

    assert decision.quality is result

    assert decision.metadata["quality_score"] == result.score

    assert decision.metadata["executor_version"] == "v9.3-m7"


def test_attempt_is_preserved():
    result = failed_quality()

    decision = QualityAwareAdaptiveExecutor().decide(
        current_strategy=SummarizationStrategyType.HIERARCHICAL,
        quality=result,
        attempt=2,
    )

    assert decision.attempt == 2
    assert decision.max_attempts == 2


def test_custom_attempt_budget_is_supported():
    result = failed_quality(score=0.20)

    decision = QualityAwareAdaptiveExecutor(
        max_attempts=3,
    ).decide(
        current_strategy=SummarizationStrategyType.HIERARCHICAL,
        quality=result,
        attempt=2,
    )

    assert decision.max_attempts == 3

    assert decision.action is AdaptiveExecutionAction.RETRY_CURRENT


@pytest.mark.parametrize(
    "attempt",
    [0, -1, 3],
)
def test_invalid_attempt_is_rejected(attempt):
    with pytest.raises(ValueError):
        QualityAwareAdaptiveExecutor(
            max_attempts=2,
        ).decide(
            current_strategy=SummarizationStrategyType.DIRECT,
            quality=failed_quality(),
            attempt=attempt,
        )


def test_invalid_strategy_is_rejected():
    with pytest.raises(TypeError):
        QualityAwareAdaptiveExecutor().decide(
            current_strategy="direct",
            quality=failed_quality(),
        )


def test_invalid_quality_is_rejected():
    with pytest.raises(TypeError):
        QualityAwareAdaptiveExecutor().decide(
            current_strategy=SummarizationStrategyType.DIRECT,
            quality=object(),
        )


def test_invalid_max_attempts_is_rejected():
    with pytest.raises(ValueError):
        QualityAwareAdaptiveExecutor(
            max_attempts=0,
        )


def test_invalid_retry_threshold_is_rejected():
    with pytest.raises(ValueError):
        QualityAwareAdaptiveExecutor(
            retry_threshold=1.1,
        )


def test_retry_threshold_must_be_numeric():
    with pytest.raises(TypeError):
        QualityAwareAdaptiveExecutor(
            retry_threshold="0.5",
        )


def test_max_attempts_must_be_integer():
    with pytest.raises(TypeError):
        QualityAwareAdaptiveExecutor(
            max_attempts=2.5,
        )
