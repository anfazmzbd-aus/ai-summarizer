"""
Tests for V9.3-M10 typed evaluation integration.
"""

from __future__ import annotations

import pytest

from app.summarization.evaluation import (
    EvaluationDimension,
    V93EvaluationRecordBuilder,
)
from app.summarization.intelligence.models import (
    DocumentProfile,
    DocumentStructureType,
)
from app.summarization.planning.adaptive_models import (
    AdaptiveStrategyDecision,
)
from app.summarization.planning.models import SummarizationPlan
from app.summarization.planning.optimization_models import (
    StrategyOptimizationDecision,
    StrategyOptimizationEstimate,
)
from app.summarization.quality.models import (
    QualityEvaluation,
    QualityMetric,
    QualityMetricName,
)
from app.summarization.quality_adaptive.models import (
    AdaptiveExecutionAction,
    AdaptiveExecutionDecision,
)
from app.summarization.resilience.models import (
    FallbackAction,
    FallbackDecision,
    ResilienceFailure,
)
from app.summarization.strategies.models import (
    StrategySelection,
    SummarizationStrategyType,
)
from app.summarization.streaming.models import StreamResult


def make_chunk():
    from app.summarization.chunking.models import Chunk

    return Chunk(
        index=0,
        text="The system processes customer requests.",
        token_count=6,
        character_count=len("The system processes customer requests."),
        start_offset=0,
        end_offset=39,
    )


def make_profile():
    return DocumentProfile(
        character_count=39,
        token_count=6,
        word_count=6,
        unique_word_count=6,
        paragraph_count=1,
        sentence_count=1,
        heading_count=0,
        list_item_count=0,
        code_block_count=0,
        quote_block_count=0,
        table_row_count=0,
        average_sentence_tokens=6.0,
        lexical_diversity=1.0,
        structure_type=DocumentStructureType.PROSE,
    )


def make_plan():
    chunk = make_chunk()

    selection = StrategySelection(
        strategy=SummarizationStrategyType.DIRECT,
        reason="deterministic test selection",
        token_count=chunk.token_count,
        chunk_count=1,
        metadata={},
    )

    return SummarizationPlan(
        strategy=SummarizationStrategyType.DIRECT,
        selection=selection,
        chunks=(chunk,),
        token_count=chunk.token_count,
        chunk_count=1,
        source_character_count=len(chunk.text),
        source_digest="test-source-digest",
        document_profile=make_profile(),
        metadata={
            "planner_version": "v9.3-m1",
        },
    )


def make_adaptive():
    return AdaptiveStrategyDecision(
        baseline_strategy=SummarizationStrategyType.DIRECT,
        selected_strategy=SummarizationStrategyType.DIRECT,
        promoted=False,
        reasons=("baseline strategy retained",),
        signals=("single_chunk",),
        metadata={
            "planner_version": "v9.3-m4",
        },
    )


def make_optimization():
    estimate = StrategyOptimizationEstimate(
        strategy=SummarizationStrategyType.DIRECT,
        input_tokens=6,
        chunk_count=1,
        estimated_input_tokens=6,
        estimated_output_tokens=3,
        estimated_total_tokens=9,
        estimated_latency_ms=100,
        estimated_cost_units=1,
        rationale=("single chunk direct execution",),
        metadata={},
    )

    return StrategyOptimizationDecision(
        baseline_strategy=SummarizationStrategyType.DIRECT,
        selected_strategy=SummarizationStrategyType.DIRECT,
        estimates=(estimate,),
        reason="direct strategy satisfies constraints",
        constrained=False,
        metadata={
            "token_budget": 100,
            "latency_budget": 1000,
            "cost_budget": 10,
        },
    )


def make_quality():
    metric = QualityMetric(
        name=QualityMetricName.NON_EMPTY,
        score=1.0,
        rationale="summary is non-empty",
        metadata={},
    )

    return QualityEvaluation(
        score=0.90,
        passed=True,
        metrics=(metric,),
        source_length=39,
        summary_length=20,
        evaluator_version="v9.3-m6",
        threshold=0.60,
        metadata={
            "deterministic": True,
        },
    )


def make_adaptive_execution():
    quality = make_quality()

    return AdaptiveExecutionDecision(
        action=AdaptiveExecutionAction.ACCEPT,
        current_strategy=SummarizationStrategyType.DIRECT,
        next_strategy=None,
        quality=quality,
        attempt=1,
        max_attempts=2,
        reason="quality threshold satisfied",
        metadata={
            "executor_version": "v9.3-m7",
        },
    )


def make_fallback():
    failure = ResilienceFailure(
        error_type="RuntimeError",
        message="test failure",
        strategy=SummarizationStrategyType.DIRECT,
        attempt=1,
        retryable=False,
        metadata={},
    )

    return FallbackDecision(
        action=FallbackAction.FALLBACK,
        failed_strategy=SummarizationStrategyType.DIRECT,
        fallback_strategy=SummarizationStrategyType.MAP_REDUCE,
        failure=failure,
        attempted_strategies=(SummarizationStrategyType.DIRECT,),
        max_attempts=3,
        reason="fallback strategy selected",
        metadata={
            "planner_version": "v9.3-m8",
        },
    )


def make_stream():
    return StreamResult(
        content="The system processes requests.",
        chunk_count=1,
        metadata={
            "streamer_version": "v9.3-m9",
            "intelligent": True,
        },
    )


def test_build_planning_record_preserves_plan_provenance():
    builder = V93EvaluationRecordBuilder()

    record = builder.build_planning_record(
        make_plan(),
        make_adaptive(),
    )

    assert record["strategy"] == "direct"
    assert record["plan"] is not None
    assert record["planner_version"] == "v9.3-m1"
    assert record["selected_strategy"] == "direct"
    assert record["promoted"] is False


def test_build_constraints_record_preserves_budgets():
    builder = V93EvaluationRecordBuilder()

    record = builder.build_constraints_record(
        make_optimization(),
    )

    assert record["token_budget"] == 100
    assert record["latency_budget"] == 1000
    assert record["cost_budget"] == 10
    assert record["constrained"] is False
    assert record["optimization"] is not None


def test_build_quality_record_preserves_quality_provenance():
    builder = V93EvaluationRecordBuilder()
    quality = make_quality()

    record = builder.build_quality_record(quality)

    assert record["score"] == quality.score
    assert record["passed"] is True
    assert record["quality"] is quality
    assert record["evaluator_version"] == "v9.3-m6"


def test_build_resilience_record_supports_m7():
    builder = V93EvaluationRecordBuilder()

    record = builder.build_resilience_record(
        make_adaptive_execution(),
    )

    assert record["action"] == "accept"
    assert record["current_strategy"] == "direct"
    assert record["adaptive_execution"] is not None


def test_build_resilience_record_supports_m8():
    builder = V93EvaluationRecordBuilder()

    record = builder.build_resilience_record(
        make_fallback(),
    )

    assert record["action"] == "fallback"
    assert record["failed_strategy"] == "direct"
    assert record["fallback_strategy"] == "map_reduce"
    assert record["fallback_decision"] is not None


def test_build_streaming_record_preserves_intelligence():
    builder = V93EvaluationRecordBuilder()

    record = builder.build_streaming_record(
        make_stream(),
    )

    assert record["intelligent"] is True
    assert record["streamer_version"] == "v9.3-m9"
    assert record["chunk_count"] == 1


def test_full_m10_evaluation_accepts_existing_v93_models():
    builder = V93EvaluationRecordBuilder()

    result = builder.evaluate(
        plan=make_plan(),
        adaptive=make_adaptive(),
        optimization=make_optimization(),
        quality=make_quality(),
        resilience=make_adaptive_execution(),
        streaming=make_stream(),
    )

    assert result.passed is True
    assert result.score == 1.0
    assert result.failures == ()
    assert all(result.dimensions[dimension] for dimension in EvaluationDimension)


def test_m10_evaluation_remains_explicit_when_optional_layers_are_missing():
    builder = V93EvaluationRecordBuilder()

    result = builder.evaluate(
        plan=make_plan(),
    )

    assert result.passed is False
    assert result.dimensions[EvaluationDimension.PLANNING] is True
    assert result.dimensions[EvaluationDimension.CONSTRAINTS] is False
    assert result.dimensions[EvaluationDimension.QUALITY] is False
    assert result.dimensions[EvaluationDimension.RESILIENCE] is False
    assert result.dimensions[EvaluationDimension.STREAMING] is False


@pytest.mark.parametrize(
    "method,value,name",
    [
        (
            "build_planning_record",
            object(),
            "plan",
        ),
        (
            "build_quality_record",
            object(),
            "quality",
        ),
        (
            "build_streaming_record",
            object(),
            "result",
        ),
    ],
)
def test_typed_adapters_reject_invalid_models(
    method,
    value,
    name,
):
    builder = V93EvaluationRecordBuilder()

    with pytest.raises(TypeError, match=name):
        getattr(builder, method)(value)


def test_constraints_adapter_rejects_invalid_model():
    builder = V93EvaluationRecordBuilder()

    with pytest.raises(TypeError, match="optimization"):
        builder.build_constraints_record(object())


def test_resilience_adapter_rejects_invalid_model():
    builder = V93EvaluationRecordBuilder()

    with pytest.raises(
        TypeError,
        match="AdaptiveExecutionDecision|FallbackDecision",
    ):
        builder.build_resilience_record(object())
