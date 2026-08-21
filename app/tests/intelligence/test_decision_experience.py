"""Tests for the V10 decision experience contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType
from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionEffectiveness,
    DecisionExperience,
    DecisionExperienceBuilder,
    EffectivenessDimension,
    EffectivenessStatus,
    EvaluationStatus,
    ExecutionFeedback,
    FeedbackSignal,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    context_id=None,
    correlation_id=None,
    action: TaskAction = TaskAction.SUMMARIZE,
    reason: str = "test decision",
    confidence: float = 1.0,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=action,
        reason=reason,
        confidence=confidence,
    )


def make_feedback(
    decision: TaskDecision,
    *,
    execution_id: str = "execution-001",
    signals: tuple[FeedbackSignal, ...] = (FeedbackSignal.SUCCESS,),
) -> ExecutionFeedback:
    return ExecutionFeedback.create(
        execution_id=execution_id,
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=signals,
    )


def make_effectiveness(
    decision: TaskDecision,
    feedback: ExecutionFeedback,
    *,
    status: EffectivenessStatus = EffectivenessStatus.EFFECTIVE,
    dimensions=None,
    reasons: tuple[str, ...] = ("execution succeeded",),
) -> DecisionEffectiveness:
    return DecisionEffectiveness.create(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        execution_id=feedback.execution_id,
        status=status,
        dimensions=(
            {
                EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            }
            if dimensions is None
            else dimensions
        ),
        reasons=reasons,
    )


def make_experience() -> DecisionExperience:
    return DecisionExperience.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_reason="test decision",
        decision_confidence=1.0,
        feedback_signals=(FeedbackSignal.SUCCESS,),
        effectiveness_status=EffectivenessStatus.EFFECTIVE,
        effectiveness_dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        },
        reasons=("execution succeeded",),
    )


def test_valid_experience_contract() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    result = DecisionExperience.create(
        context_id=context_id,
        correlation_id=correlation_id,
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_reason="summarize document",
        decision_confidence=0.9,
        feedback_signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
        effectiveness_status=EffectivenessStatus.DEGRADED,
        effectiveness_dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
        },
        reasons=("execution required retries",),
        metadata={"source": "test"},
    )

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id
    assert result.execution_id == "execution-001"
    assert result.action is TaskAction.SUMMARIZE
    assert result.decision_reason == "summarize document"
    assert result.decision_confidence == 0.9
    assert result.feedback_signals == (
        FeedbackSignal.SUCCESS,
        FeedbackSignal.RETRY_OBSERVED,
    )
    assert result.effectiveness_status is EffectivenessStatus.DEGRADED


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        DecisionExperience.create(
            context_id="invalid",
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id="invalid",
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_execution_id_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="execution_id must be a string",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id=123,
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_execution_id_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="execution_id must not be empty",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action="summarize",
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_decision_reason_must_be_string() -> None:
    with pytest.raises(
        TypeError,
        match="decision_reason must be a string",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason=123,
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_decision_reason_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="decision_reason must not be empty",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


@pytest.mark.parametrize(
    "value",
    [
        "high",
        None,
        True,
    ],
)
def test_decision_confidence_must_be_numeric(value) -> None:
    with pytest.raises(
        TypeError,
        match="decision_confidence must be a number",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=value,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


@pytest.mark.parametrize(
    "value",
    [-0.01, 1.01],
)
def test_decision_confidence_range_is_validated(value: float) -> None:
    with pytest.raises(
        ValueError,
        match="decision_confidence must be between 0 and 1",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=value,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
        )


def test_integer_confidence_is_normalized_to_float() -> None:
    result = DecisionExperience.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_reason="reason",
        decision_confidence=1,
        feedback_signals=(),
        effectiveness_status=EffectivenessStatus.UNKNOWN,
        effectiveness_dimensions={},
    )

    assert result.decision_confidence == 1.0
    assert isinstance(result.decision_confidence, float)


def test_feedback_signals_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="feedback_signals must be a tuple",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=[FeedbackSignal.SUCCESS],
            effectiveness_status=EffectivenessStatus.EFFECTIVE,
            effectiveness_dimensions={},
        )


def test_feedback_signals_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="FeedbackSignal values",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=("success",),
            effectiveness_status=EffectivenessStatus.EFFECTIVE,
            effectiveness_dimensions={},
        )


def test_duplicate_feedback_signals_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="must not contain duplicates",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(
                FeedbackSignal.SUCCESS,
                FeedbackSignal.SUCCESS,
            ),
            effectiveness_status=EffectivenessStatus.EFFECTIVE,
            effectiveness_dimensions={},
        )


def test_effectiveness_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="effectiveness_status must be an EffectivenessStatus",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status="effective",
            effectiveness_dimensions={},
        )


def test_effectiveness_dimensions_must_be_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="effectiveness_dimensions must be a mapping",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions=[],
        )


def test_effectiveness_dimension_keys_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="EffectivenessDimension values",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={
                "outcome": EffectivenessStatus.EFFECTIVE,
            },
        )


def test_effectiveness_dimension_values_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="EffectivenessStatus values",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={
                EffectivenessDimension.OUTCOME: "effective",
            },
        )


def test_effectiveness_dimensions_are_immutable() -> None:
    result = make_experience()

    assert isinstance(
        result.effectiveness_dimensions,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        result.effectiveness_dimensions[EffectivenessDimension.OUTCOME] = (
            EffectivenessStatus.DEGRADED
        )


def test_effectiveness_dimensions_are_defensively_copied() -> None:
    dimensions = {
        EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
    }

    result = DecisionExperience.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_reason="reason",
        decision_confidence=1.0,
        feedback_signals=(FeedbackSignal.SUCCESS,),
        effectiveness_status=EffectivenessStatus.EFFECTIVE,
        effectiveness_dimensions=dimensions,
    )

    dimensions[EffectivenessDimension.OUTCOME] = EffectivenessStatus.INEFFECTIVE

    assert (
        result.effectiveness_dimensions[EffectivenessDimension.OUTCOME]
        is EffectivenessStatus.EFFECTIVE
    )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
            reasons=(123,),
        )


def test_metadata_must_be_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="metadata must be a mapping",
    ):
        DecisionExperience.create(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_reason="reason",
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions={},
            metadata=[],
        )


def test_metadata_is_immutable() -> None:
    result = DecisionExperience.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_reason="reason",
        decision_confidence=1.0,
        feedback_signals=(),
        effectiveness_status=EffectivenessStatus.UNKNOWN,
        effectiveness_dimensions={},
        metadata={"source": "test"},
    )

    assert isinstance(result.metadata, MappingProxyType)

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_metadata_is_defensively_copied() -> None:
    metadata = {"source": "original"}

    result = DecisionExperience.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_reason="reason",
        decision_confidence=1.0,
        feedback_signals=(),
        effectiveness_status=EffectivenessStatus.UNKNOWN,
        effectiveness_dimensions={},
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert result.metadata["source"] == "original"


def test_contract_is_frozen() -> None:
    result = make_experience()

    with pytest.raises(FrozenInstanceError):
        result.action = TaskAction.RETRY


def test_builder_returns_decision_experience() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert isinstance(result, DecisionExperience)


def test_builder_preserves_decision_fields() -> None:
    decision = make_decision(
        action=TaskAction.VERIFY,
        reason="verify result",
        confidence=0.75,
    )
    feedback = make_feedback(decision)
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert result.action is TaskAction.VERIFY
    assert result.decision_reason == "verify result"
    assert result.decision_confidence == 0.75


def test_builder_preserves_feedback_signals() -> None:
    decision = make_decision()
    feedback = make_feedback(
        decision,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
    )
    effectiveness = make_effectiveness(
        decision,
        feedback,
        status=EffectivenessStatus.DEGRADED,
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert result.feedback_signals == feedback.signals


def test_builder_preserves_effectiveness() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)

    dimensions = {
        EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
    }

    effectiveness = make_effectiveness(
        decision,
        feedback,
        status=EffectivenessStatus.DEGRADED,
        dimensions=dimensions,
        reasons=("reliability degraded",),
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert result.effectiveness_status is EffectivenessStatus.DEGRADED
    assert dict(result.effectiveness_dimensions) == dimensions
    assert result.reasons == ("reliability degraded",)


def test_builder_preserves_execution_provenance() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
    )
    feedback = make_feedback(
        decision,
        execution_id="execution-special",
    )
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert result.context_id == context_id
    assert result.correlation_id == correlation_id
    assert result.execution_id == "execution-special"


def test_builder_accepts_explicit_metadata() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
        metadata={"source": "m4.3"},
    )

    assert result.metadata["source"] == "m4.3"


def test_builder_does_not_merge_input_metadata() -> None:
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
        metadata={"feedback": "metadata"},
    )

    effectiveness = DecisionEffectiveness.create(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        execution_id=feedback.execution_id,
        status=EffectivenessStatus.EFFECTIVE,
        metadata={"effectiveness": "metadata"},
    )

    result = DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert result.metadata == {}


def test_invalid_decision_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        DecisionExperienceBuilder().build(
            "invalid",
            feedback,
            effectiveness,
        )


def test_invalid_feedback_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    with pytest.raises(
        TypeError,
        match="feedback must be an ExecutionFeedback",
    ):
        DecisionExperienceBuilder().build(
            decision,
            "invalid",
            effectiveness,
        )


def test_invalid_effectiveness_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)

    with pytest.raises(
        TypeError,
        match="effectiveness must be a DecisionEffectiveness",
    ):
        DecisionExperienceBuilder().build(
            decision,
            feedback,
            "invalid",
        )


def test_decision_feedback_context_mismatch_is_rejected() -> None:
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    effectiveness = DecisionEffectiveness.create(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        execution_id=feedback.execution_id,
        status=EffectivenessStatus.EFFECTIVE,
    )

    with pytest.raises(
        ValueError,
        match="decision and feedback context_id must match",
    ):
        DecisionExperienceBuilder().build(
            decision,
            feedback,
            effectiveness,
        )


def test_decision_effectiveness_context_mismatch_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)

    effectiveness = DecisionEffectiveness.create(
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
        execution_id=feedback.execution_id,
        status=EffectivenessStatus.EFFECTIVE,
    )

    with pytest.raises(
        ValueError,
        match="decision and effectiveness context_id must match",
    ):
        DecisionExperienceBuilder().build(
            decision,
            feedback,
            effectiveness,
        )


def test_decision_feedback_correlation_mismatch_is_rejected() -> None:
    decision = make_decision()

    feedback = ExecutionFeedback.create(
        execution_id="execution-001",
        context_id=decision.context_id,
        correlation_id=uuid4(),
        evaluation_status=EvaluationStatus.PASS,
        signals=(FeedbackSignal.SUCCESS,),
    )

    effectiveness = DecisionEffectiveness.create(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        execution_id=feedback.execution_id,
        status=EffectivenessStatus.EFFECTIVE,
    )

    with pytest.raises(
        ValueError,
        match="decision and feedback correlation_id must match",
    ):
        DecisionExperienceBuilder().build(
            decision,
            feedback,
            effectiveness,
        )


def test_decision_effectiveness_correlation_mismatch_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)

    effectiveness = DecisionEffectiveness.create(
        context_id=decision.context_id,
        correlation_id=uuid4(),
        execution_id=feedback.execution_id,
        status=EffectivenessStatus.EFFECTIVE,
    )

    with pytest.raises(
        ValueError,
        match="decision and effectiveness correlation_id must match",
    ):
        DecisionExperienceBuilder().build(
            decision,
            feedback,
            effectiveness,
        )


def test_execution_id_mismatch_is_rejected() -> None:
    decision = make_decision()
    feedback = make_feedback(
        decision,
        execution_id="execution-A",
    )

    effectiveness = DecisionEffectiveness.create(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        execution_id="execution-B",
        status=EffectivenessStatus.EFFECTIVE,
    )

    with pytest.raises(
        ValueError,
        match="feedback and effectiveness execution_id must match",
    ):
        DecisionExperienceBuilder().build(
            decision,
            feedback,
            effectiveness,
        )


def test_builder_is_deterministic() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision(
        context_id=context_id,
        correlation_id=correlation_id,
        confidence=0.8,
    )

    feedback = make_feedback(
        decision,
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        ),
    )

    effectiveness = make_effectiveness(
        decision,
        feedback,
        status=EffectivenessStatus.DEGRADED,
        dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
        },
        reasons=("execution required retries",),
    )

    builder = DecisionExperienceBuilder()

    first = builder.build(
        decision,
        feedback,
        effectiveness,
        metadata={"source": "test"},
    )
    second = builder.build(
        decision,
        feedback,
        effectiveness,
        metadata={"source": "test"},
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    decision = make_decision()
    feedback = make_feedback(decision)
    effectiveness = make_effectiveness(
        decision,
        feedback,
    )

    decision_before = decision
    feedback_before = feedback
    effectiveness_before = effectiveness

    DecisionExperienceBuilder().build(
        decision,
        feedback,
        effectiveness,
    )

    assert decision == decision_before
    assert feedback == feedback_before
    assert effectiveness == effectiveness_before


def test_contract_contains_no_storage_or_runtime_fields() -> None:
    forbidden_fields = {
        "repository",
        "database",
        "provider",
        "runtime",
        "executor",
        "callback",
        "created_at",
        "reward",
        "penalty",
        "learning_weight",
    }

    assert not (forbidden_fields & set(DecisionExperience.__dataclass_fields__))


def test_builder_has_no_adaptive_or_persistence_interface() -> None:
    forbidden_methods = {
        "execute",
        "persist",
        "save",
        "retry",
        "replan",
        "adapt",
        "learn",
        "switch_provider",
        "select_strategy",
    }

    public_names = {
        name for name in dir(DecisionExperienceBuilder) if not name.startswith("_")
    }

    assert not (forbidden_methods & public_names)


def test_builder_exposes_only_build_as_public_method() -> None:
    public_methods = {
        name for name in dir(DecisionExperienceBuilder) if not name.startswith("_")
    }

    assert public_methods == {"build"}
