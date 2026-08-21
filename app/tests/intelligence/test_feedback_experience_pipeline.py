"""Tests for the V10 feedback-to-experience pipeline."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionEffectiveness,
    DecisionExperience,
    EffectivenessDimension,
    EffectivenessStatus,
    EvaluationStatus,
    ExecutionFeedback,
    FeedbackExperiencePipeline,
    FeedbackExperienceResult,
    FeedbackSignal,
    InMemoryExperienceRepository,
    NormalizedDecisionExperience,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    context_id=None,
    correlation_id=None,
    confidence: float = 1.0,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=TaskAction.SUMMARIZE,
        reason="test decision",
        confidence=confidence,
    )


def make_feedback(
    decision: TaskDecision,
    *,
    execution_id: str = "execution-001",
    evaluation_status: EvaluationStatus = EvaluationStatus.PASS,
    signals: tuple[FeedbackSignal, ...] = (FeedbackSignal.SUCCESS,),
) -> ExecutionFeedback:
    return ExecutionFeedback.create(
        execution_id=execution_id,
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        evaluation_status=evaluation_status,
        signals=signals,
    )


def test_pipeline_returns_result() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert isinstance(
        result,
        FeedbackExperienceResult,
    )


def test_result_contains_effectiveness() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert isinstance(
        result.effectiveness,
        DecisionEffectiveness,
    )


def test_result_contains_decision_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert isinstance(
        result.experience,
        DecisionExperience,
    )


def test_result_contains_normalized_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert isinstance(
        result.normalized_experience,
        NormalizedDecisionExperience,
    )


def test_successful_feedback_produces_effective_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(
        decision,
        signals=(FeedbackSignal.SUCCESS,),
    )

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert result.effectiveness.status is EffectivenessStatus.EFFECTIVE

    assert result.experience.effectiveness_status is EffectivenessStatus.EFFECTIVE

    assert (
        result.normalized_experience.effectiveness_status
        is EffectivenessStatus.EFFECTIVE
    )


def test_degraded_feedback_produces_degraded_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    feedback = make_feedback(
        decision,
        evaluation_status=EvaluationStatus.DEGRADED,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
    )

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert result.effectiveness.status is EffectivenessStatus.DEGRADED

    assert (
        result.normalized_experience.effectiveness_status
        is EffectivenessStatus.DEGRADED
    )


def test_retry_degrades_reliability_dimension() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    feedback = make_feedback(
        decision,
        evaluation_status=EvaluationStatus.DEGRADED,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
    )

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    dimensions = dict(result.normalized_experience.effectiveness_dimensions)

    assert (
        dimensions[EffectivenessDimension.RELIABILITY] is EffectivenessStatus.DEGRADED
    )


def test_failed_feedback_produces_ineffective_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    feedback = make_feedback(
        decision,
        evaluation_status=EvaluationStatus.FAIL,
        signals=(FeedbackSignal.EXECUTION_FAILED,),
    )

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert result.effectiveness.status is EffectivenessStatus.INEFFECTIVE


def test_pipeline_stores_normalized_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert repository.list_all() == (result.normalized_experience,)


def test_stored_experience_is_available_by_provenance() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    feedback = make_feedback(
        decision,
        execution_id="execution-special",
    )

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    stored = repository.get(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        execution_id="execution-special",
    )

    assert stored == result.normalized_experience


def test_stored_experience_is_available_by_comparison_key() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    matches = repository.find_by_comparison_key(
        result.normalized_experience.comparison_key
    )

    assert matches == (result.normalized_experience,)


def test_pipeline_preserves_context_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    repository = InMemoryExperienceRepository()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    feedback = make_feedback(
        decision,
        execution_id="execution-special",
    )

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert result.effectiveness.context_id == context_id
    assert result.experience.context_id == context_id
    assert result.normalized_experience.context_id == context_id

    assert result.normalized_experience.correlation_id == correlation_id

    assert result.normalized_experience.execution_id == "execution-special"


def test_pipeline_preserves_decision_fields() -> None:
    repository = InMemoryExperienceRepository()

    decision = make_decision(
        confidence=0.75,
    )
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    assert result.experience.action is decision.action
    assert result.experience.decision_reason == decision.reason
    assert result.experience.decision_confidence == 0.75


def test_pipeline_passes_explicit_metadata_to_experience() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
        metadata={"source": "m4.6"},
    )

    assert result.experience.metadata["source"] == "m4.6"


def test_normalized_experience_excludes_metadata() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
        metadata={"source": "m4.6"},
    )

    assert not hasattr(
        result.normalized_experience,
        "metadata",
    )


def test_pipeline_rejects_invalid_decision() -> None:
    repository = InMemoryExperienceRepository()

    decision = make_decision()
    feedback = make_feedback(decision)

    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        FeedbackExperiencePipeline(
            repository=repository,
        ).process(
            "invalid",
            feedback,
        )


def test_pipeline_rejects_invalid_feedback() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    with pytest.raises(
        TypeError,
        match="feedback must be an ExecutionFeedback",
    ):
        FeedbackExperiencePipeline(
            repository=repository,
        ).process(
            decision,
            "invalid",
        )


def test_pipeline_rejects_invalid_metadata() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    with pytest.raises(
        TypeError,
        match="metadata must be a mapping or None",
    ):
        FeedbackExperiencePipeline(
            repository=repository,
        ).process(
            decision,
            feedback,
            metadata=[],
        )


def test_pipeline_rejects_invalid_repository() -> None:
    with pytest.raises(
        TypeError,
        match="repository must satisfy ExperienceRepository",
    ):
        FeedbackExperiencePipeline(
            repository=object(),
        )


def test_pipeline_propagates_context_mismatch_validation() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    with pytest.raises(
        ValueError,
        match="context_id must match",
    ):
        FeedbackExperiencePipeline(
            repository=repository,
        ).process(
            decision,
            feedback,
        )


def test_pipeline_propagates_correlation_mismatch_validation() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=decision.context_id,
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    with pytest.raises(
        ValueError,
        match="correlation_id must match",
    ):
        FeedbackExperiencePipeline(
            repository=repository,
        ).process(
            decision,
            feedback,
        )


def test_duplicate_execution_is_not_silently_overwritten() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    pipeline = FeedbackExperiencePipeline(
        repository=repository,
    )

    pipeline.process(
        decision,
        feedback,
    )

    with pytest.raises(
        ValueError,
        match="experience provenance already exists",
    ):
        pipeline.process(
            decision,
            feedback,
        )


def test_pipeline_result_is_frozen() -> None:
    repository = InMemoryExperienceRepository()
    decision = make_decision()
    feedback = make_feedback(decision)

    result = FeedbackExperiencePipeline(
        repository=repository,
    ).process(
        decision,
        feedback,
    )

    with pytest.raises(FrozenInstanceError):
        result.experience = None


def test_pipeline_is_deterministic_before_repository_write() -> None:
    first_repository = InMemoryExperienceRepository()
    second_repository = InMemoryExperienceRepository()

    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    feedback = make_feedback(
        decision,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
    )

    first = FeedbackExperiencePipeline(
        repository=first_repository,
    ).process(
        decision,
        feedback,
        metadata={"source": "test"},
    )

    second = FeedbackExperiencePipeline(
        repository=second_repository,
    ).process(
        decision,
        feedback,
        metadata={"source": "test"},
    )

    assert first == second


def test_pipeline_has_no_runtime_or_learning_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "adapt",
        "learn",
        "switch_provider",
        "select_strategy",
        "similarity_search",
    }

    public_names = {
        name for name in dir(FeedbackExperiencePipeline) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_pipeline_exposes_only_process() -> None:
    public_names = {
        name for name in dir(FeedbackExperiencePipeline) if not name.startswith("_")
    }

    assert public_names == {"process"}
