"""
Tests for V9.3-M6 quality models.
"""

from __future__ import annotations

import pytest

from app.summarization.quality.models import (
    QualityEvaluation,
    QualityMetric,
    QualityMetricName,
)


def metric(
    name=QualityMetricName.NON_EMPTY,
    score=1.0,
):
    return QualityMetric(
        name=name,
        score=score,
        rationale="test",
        metadata={},
    )


def test_quality_metric_is_immutable():
    value = metric()

    with pytest.raises(AttributeError):
        value.score = 0.0


def test_quality_metric_accepts_boundary_scores():
    assert metric(score=0.0).score == 0.0
    assert metric(score=1.0).score == 1.0


@pytest.mark.parametrize(
    "score",
    [-0.01, 1.01],
)
def test_quality_metric_rejects_invalid_score(score):
    with pytest.raises(ValueError):
        metric(score=score)


def test_quality_metric_rejects_invalid_name():
    with pytest.raises(TypeError):
        QualityMetric(
            name="coverage",
            score=1.0,
            rationale="test",
            metadata={},
        )


def test_quality_metric_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        QualityMetric(
            name=QualityMetricName.COVERAGE,
            score=1.0,
            rationale="test",
            metadata=[],
        )


def test_quality_evaluation_is_immutable():
    evaluation = QualityEvaluation(
        score=0.8,
        passed=True,
        metrics=(metric(),),
        source_length=100,
        summary_length=30,
    )

    with pytest.raises(AttributeError):
        evaluation.score = 0.2


def test_quality_evaluation_accepts_empty_source():
    evaluation = QualityEvaluation(
        score=0.5,
        passed=False,
        metrics=(metric(),),
        source_length=0,
        summary_length=0,
    )

    assert evaluation.source_length == 0


def test_quality_evaluation_rejects_empty_metrics():
    with pytest.raises(ValueError):
        QualityEvaluation(
            score=0.5,
            passed=False,
            metrics=(),
            source_length=10,
            summary_length=5,
        )


@pytest.mark.parametrize(
    "score",
    [-0.01, 1.01],
)
def test_quality_evaluation_rejects_invalid_score(
    score,
):
    with pytest.raises(ValueError):
        QualityEvaluation(
            score=score,
            passed=False,
            metrics=(metric(),),
            source_length=10,
            summary_length=5,
        )


def test_quality_evaluation_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        QualityEvaluation(
            score=0.5,
            passed=False,
            metrics=(metric(),),
            source_length=10,
            summary_length=5,
            threshold=1.1,
        )
