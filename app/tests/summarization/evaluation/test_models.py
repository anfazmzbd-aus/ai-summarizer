"""
Tests for V9.3-M10 evaluation models.
"""

from __future__ import annotations

import pytest

from app.summarization.evaluation.models import (
    EvaluationDimension,
    EvaluationResult,
)


def valid_dimensions():
    return {
        EvaluationDimension.PLANNING: True,
        EvaluationDimension.CONSTRAINTS: True,
        EvaluationDimension.QUALITY: True,
        EvaluationDimension.RESILIENCE: True,
        EvaluationDimension.STREAMING: True,
    }


def test_evaluation_result_is_immutable():
    result = EvaluationResult(
        passed=True,
        dimensions=valid_dimensions(),
        score=1.0,
    )

    with pytest.raises(AttributeError):
        result.passed = False  # type: ignore[misc]


def test_evaluation_result_accepts_valid_result():
    result = EvaluationResult(
        passed=True,
        dimensions=valid_dimensions(),
        score=1.0,
    )

    assert result.passed is True
    assert result.score == 1.0
    assert result.failures == ()


def test_failed_dimensions_are_preserved():
    dimensions = valid_dimensions()
    dimensions[EvaluationDimension.QUALITY] = False

    result = EvaluationResult(
        passed=False,
        dimensions=dimensions,
        score=0.8,
        failures=("quality",),
    )

    assert result.passed is False
    assert result.failures == ("quality",)


def test_invalid_score_type_is_rejected():
    with pytest.raises(TypeError):
        EvaluationResult(
            passed=True,
            dimensions=valid_dimensions(),
            score="1.0",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "score",
    [-0.1, 1.1],
)
def test_invalid_score_range_is_rejected(score):
    with pytest.raises(ValueError):
        EvaluationResult(
            passed=True,
            dimensions=valid_dimensions(),
            score=score,
        )


def test_invalid_dimension_key_is_rejected():
    with pytest.raises(TypeError):
        EvaluationResult(
            passed=True,
            dimensions={
                "planning": True,  # type: ignore[dict-item]
            },
            score=1.0,
        )


def test_invalid_dimension_value_is_rejected():
    with pytest.raises(TypeError):
        EvaluationResult(
            passed=True,
            dimensions={
                EvaluationDimension.PLANNING: "yes",  # type: ignore[dict-item]
            },
            score=1.0,
        )


def test_passed_must_match_dimensions():
    dimensions = valid_dimensions()
    dimensions[EvaluationDimension.QUALITY] = False

    with pytest.raises(ValueError):
        EvaluationResult(
            passed=True,
            dimensions=dimensions,
            score=0.8,
            failures=("quality",),
        )


def test_failures_must_match_dimensions():
    dimensions = valid_dimensions()
    dimensions[EvaluationDimension.QUALITY] = False

    with pytest.raises(ValueError):
        EvaluationResult(
            passed=False,
            dimensions=dimensions,
            score=0.8,
            failures=(),
        )


def test_failures_must_be_tuple():
    with pytest.raises(TypeError):
        EvaluationResult(
            passed=True,
            dimensions=valid_dimensions(),
            score=1.0,
            failures=[],  # type: ignore[arg-type]
        )


def test_metadata_must_be_dictionary():
    with pytest.raises(TypeError):
        EvaluationResult(
            passed=True,
            dimensions=valid_dimensions(),
            score=1.0,
            metadata=[],  # type: ignore[arg-type]
        )
