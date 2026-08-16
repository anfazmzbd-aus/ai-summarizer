"""
Tests for V9.3-M6 deterministic quality evaluation.
"""

from __future__ import annotations

import pytest

from app.summarization.quality import (
    QualityMetricName,
    SummarizationQualityEvaluator,
)


def test_evaluator_is_deterministic():
    source = (
        "The platform processes customer requests "
        "through an automated summarization service."
    )

    summary = "The platform processes customer requests " "through summarization."

    evaluator = SummarizationQualityEvaluator()

    first = evaluator.evaluate(
        source,
        summary,
    )

    second = evaluator.evaluate(
        source,
        summary,
    )

    assert first == second


def test_non_empty_summary_receives_full_non_empty_score():
    result = SummarizationQualityEvaluator().evaluate(
        "Source document.",
        "A useful summary.",
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.NON_EMPTY
    )

    assert metric.score == 1.0


def test_empty_summary_fails_non_empty_metric():
    result = SummarizationQualityEvaluator().evaluate(
        "Source document.",
        "",
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.NON_EMPTY
    )

    assert metric.score == 0.0


def test_short_summary_receives_compression_credit():
    source = "A" * 1000
    summary = "A" * 200

    result = SummarizationQualityEvaluator().evaluate(
        source,
        summary,
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.COMPRESSION
    )

    assert metric.score == 1.0


def test_summary_larger_than_source_has_no_compression_credit():
    source = "short source"
    summary = "this summary is considerably longer than source"

    result = SummarizationQualityEvaluator().evaluate(
        source,
        summary,
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.COMPRESSION
    )

    assert metric.score == 0.0


def test_summary_terms_are_measured_against_source():
    source = "The system processes customer requests " "using automated summarization."

    summary = "The system processes customer requests."

    result = SummarizationQualityEvaluator().evaluate(
        source,
        summary,
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.COVERAGE
    )

    assert metric.score == 1.0


def test_unrelated_summary_has_low_coverage():
    source = "The system processes customer requests."

    summary = "Weather forecasts discuss rainfall."

    result = SummarizationQualityEvaluator().evaluate(
        source,
        summary,
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.COVERAGE
    )

    assert metric.score == 0.0


def test_repetition_penalty_is_applied():
    source = "The system processes requests."

    summary = "system system system system"

    result = SummarizationQualityEvaluator().evaluate(
        source,
        summary,
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.REPETITION
    )

    assert metric.score < 1.0


def test_normal_summary_has_good_repetition_score():
    source = "The system processes customer requests."

    summary = "The system processes customer requests."

    result = SummarizationQualityEvaluator().evaluate(
        source,
        summary,
    )

    metric = next(
        item for item in result.metrics if item.name is QualityMetricName.REPETITION
    )

    assert metric.score == 1.0


def test_evaluation_contains_all_quality_dimensions():
    result = SummarizationQualityEvaluator().evaluate(
        "The source contains useful information.",
        "The source contains information.",
    )

    names = {metric.name for metric in result.metrics}

    assert names == {
        QualityMetricName.NON_EMPTY,
        QualityMetricName.COMPRESSION,
        QualityMetricName.COVERAGE,
        QualityMetricName.REPETITION,
    }


def test_aggregate_score_is_between_zero_and_one():
    result = SummarizationQualityEvaluator().evaluate(
        "A source document with information.",
        "A summary with information.",
    )

    assert 0.0 <= result.score <= 1.0


def test_threshold_controls_pass_status():
    evaluator = SummarizationQualityEvaluator(
        threshold=0.0,
    )

    result = evaluator.evaluate(
        "Source.",
        "",
    )

    assert result.passed is True


def test_default_threshold_is_recorded():
    result = SummarizationQualityEvaluator().evaluate(
        "Source.",
        "Summary.",
    )

    assert result.threshold == 0.60


def test_custom_threshold_is_recorded():
    result = SummarizationQualityEvaluator(
        threshold=0.80,
    ).evaluate(
        "Source.",
        "Summary.",
    )

    assert result.threshold == 0.80


def test_evaluator_is_provider_independent():
    evaluator = SummarizationQualityEvaluator()

    result = evaluator.evaluate(
        "Provider independent source.",
        "Provider independent summary.",
    )

    assert result.metadata["deterministic"] is True
    assert result.evaluator_version == "v9.3-m6"


@pytest.mark.parametrize(
    "source",
    [None, 123, [], {}],
)
def test_evaluator_rejects_invalid_source(source):
    with pytest.raises(TypeError):
        SummarizationQualityEvaluator().evaluate(
            source,
            "summary",
        )


@pytest.mark.parametrize(
    "summary",
    [None, 123, [], {}],
)
def test_evaluator_rejects_invalid_summary(summary):
    with pytest.raises(TypeError):
        SummarizationQualityEvaluator().evaluate(
            "source",
            summary,
        )


@pytest.mark.parametrize(
    "threshold",
    [-0.1, 1.1],
)
def test_evaluator_rejects_invalid_threshold(
    threshold,
):
    with pytest.raises(ValueError):
        SummarizationQualityEvaluator(
            threshold=threshold,
        )


def test_empty_source_and_empty_summary_are_deterministic():
    result = SummarizationQualityEvaluator().evaluate(
        "",
        "",
    )

    assert result.source_length == 0
    assert result.summary_length == 0
    assert result.score >= 0.0
    assert result.score <= 1.0
