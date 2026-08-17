"""
Tests for V9.3-M10 production evaluation.
"""

from __future__ import annotations

import pytest

from app.summarization.evaluation import (
    EvaluationDimension,
    SummarizationEvaluationEvaluator,
)


def complete_execution_record():
    return {
        "planning": {
            "planner_version": "v9.3-m1",
            "strategy": "map_reduce",
        },
        "constraints": {
            "token_budget": 4096,
            "latency_budget": 1000,
            "cost_budget": 0.01,
        },
        "quality": {
            "score": 0.85,
            "passed": True,
        },
        "resilience": {
            "action": "accept",
            "fallback_used": False,
        },
        "streaming": {
            "streamer_version": "v9.3-m9",
            "intelligent": True,
        },
    }


def test_complete_execution_record_passes():
    result = SummarizationEvaluationEvaluator().evaluate(**complete_execution_record())

    assert result.passed is True
    assert result.score == 1.0
    assert result.failures == ()


def test_all_dimensions_are_evaluated():
    result = SummarizationEvaluationEvaluator().evaluate(**complete_execution_record())

    assert set(result.dimensions) == {
        EvaluationDimension.PLANNING,
        EvaluationDimension.CONSTRAINTS,
        EvaluationDimension.QUALITY,
        EvaluationDimension.RESILIENCE,
        EvaluationDimension.STREAMING,
    }


def test_evaluator_is_deterministic():
    record = complete_execution_record()
    evaluator = SummarizationEvaluationEvaluator()

    first = evaluator.evaluate(**record)
    second = evaluator.evaluate(**record)

    assert first == second


def test_missing_planning_fails():
    record = complete_execution_record()
    record.pop("planning")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "planning" in result.failures


def test_missing_constraints_fails():
    record = complete_execution_record()
    record.pop("constraints")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "constraints" in result.failures


def test_missing_quality_fails():
    record = complete_execution_record()
    record.pop("quality")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "quality" in result.failures


def test_missing_resilience_fails():
    record = complete_execution_record()
    record.pop("resilience")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "resilience" in result.failures


def test_missing_streaming_fails():
    record = complete_execution_record()
    record.pop("streaming")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "streaming" in result.failures


def test_quality_score_must_be_valid():
    record = complete_execution_record()
    record["quality"]["score"] = 1.5

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "quality" in result.failures


def test_planning_requires_strategy():
    record = complete_execution_record()
    record["planning"].pop("strategy")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.passed is False
    assert "planning" in result.failures


def test_constraints_accept_token_budget():
    record = complete_execution_record()
    record["constraints"] = {
        "token_budget": 4096,
    }

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.dimensions[EvaluationDimension.CONSTRAINTS] is True


def test_constraints_accept_latency_budget():
    record = complete_execution_record()
    record["constraints"] = {
        "latency_budget": 1000,
    }

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.dimensions[EvaluationDimension.CONSTRAINTS] is True


def test_constraints_accept_cost_budget():
    record = complete_execution_record()
    record["constraints"] = {
        "cost_budget": 0.01,
    }

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.dimensions[EvaluationDimension.CONSTRAINTS] is True


def test_resilience_accepts_fallback_state():
    record = complete_execution_record()
    record["resilience"] = {
        "fallback_used": True,
    }

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.dimensions[EvaluationDimension.RESILIENCE] is True


def test_streaming_accepts_intelligence_metadata():
    record = complete_execution_record()
    record["streaming"] = {
        "intelligence": {
            "planner": {
                "planner_version": "v9.3-m1",
            },
        },
    }

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.dimensions[EvaluationDimension.STREAMING] is True


def test_invalid_planning_mapping_is_rejected():
    with pytest.raises(TypeError):
        SummarizationEvaluationEvaluator().evaluate(
            planning="invalid",  # type: ignore[arg-type]
        )


def test_invalid_constraints_mapping_is_rejected():
    with pytest.raises(TypeError):
        SummarizationEvaluationEvaluator().evaluate(
            constraints="invalid",  # type: ignore[arg-type]
        )


def test_invalid_quality_mapping_is_rejected():
    with pytest.raises(TypeError):
        SummarizationEvaluationEvaluator().evaluate(
            quality="invalid",  # type: ignore[arg-type]
        )


def test_invalid_resilience_mapping_is_rejected():
    with pytest.raises(TypeError):
        SummarizationEvaluationEvaluator().evaluate(
            resilience="invalid",  # type: ignore[arg-type]
        )


def test_invalid_streaming_mapping_is_rejected():
    with pytest.raises(TypeError):
        SummarizationEvaluationEvaluator().evaluate(
            streaming="invalid",  # type: ignore[arg-type]
        )


def test_metadata_contains_evaluator_version():
    result = SummarizationEvaluationEvaluator().evaluate(**complete_execution_record())

    assert result.metadata["evaluator_version"] == "v9.3-m10"


def test_metadata_marks_evaluation_deterministic():
    result = SummarizationEvaluationEvaluator().evaluate(**complete_execution_record())

    assert result.metadata["deterministic"] is True


def test_score_is_fraction_of_passing_dimensions():
    record = complete_execution_record()
    record.pop("quality")

    result = SummarizationEvaluationEvaluator().evaluate(**record)

    assert result.score == 0.8


def test_evaluation_has_no_provider_dependency():
    evaluator = SummarizationEvaluationEvaluator()

    result = evaluator.evaluate(
        planning={
            "planner_version": "v9.3-m1",
            "strategy": "direct",
        },
        constraints={
            "token_budget": 2048,
        },
        quality={
            "score": 0.9,
        },
        resilience={
            "action": "accept",
        },
        streaming={
            "streamer_version": "v9.3-m9",
        },
    )

    assert result.passed is True
