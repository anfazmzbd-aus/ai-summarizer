"""Tests for V10 decision experience normalization."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    DecisionExperience,
    EffectivenessDimension,
    EffectivenessStatus,
    ExperienceNormalizer,
    FeedbackSignal,
    NormalizedDecisionExperience,
    TaskAction,
)


def make_experience(
    *,
    context_id=None,
    correlation_id=None,
    execution_id: str = "execution-001",
    action: TaskAction = TaskAction.SUMMARIZE,
    confidence: float = 0.8,
    signals: tuple[FeedbackSignal, ...] = (FeedbackSignal.SUCCESS,),
    status: EffectivenessStatus = EffectivenessStatus.EFFECTIVE,
    dimensions=None,
    reason: str = "free-form decision reason",
    reasons: tuple[str, ...] = ("free-form effectiveness reason",),
    metadata=None,
) -> DecisionExperience:
    return DecisionExperience.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        execution_id=execution_id,
        action=action,
        decision_reason=reason,
        decision_confidence=confidence,
        feedback_signals=signals,
        effectiveness_status=status,
        effectiveness_dimensions=(
            {
                EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            }
            if dimensions is None
            else dimensions
        ),
        reasons=reasons,
        metadata={} if metadata is None else metadata,
    )


def test_normalizer_returns_normalized_experience() -> None:
    result = ExperienceNormalizer().normalize(make_experience())

    assert isinstance(
        result,
        NormalizedDecisionExperience,
    )


def test_normalizer_preserves_context_id() -> None:
    context_id = uuid4()

    result = ExperienceNormalizer().normalize(make_experience(context_id=context_id))

    assert result.context_id == context_id


def test_normalizer_preserves_correlation_id() -> None:
    correlation_id = uuid4()

    result = ExperienceNormalizer().normalize(
        make_experience(
            correlation_id=correlation_id,
        )
    )

    assert result.correlation_id == correlation_id


def test_normalizer_preserves_execution_id() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            execution_id="execution-special",
        )
    )

    assert result.execution_id == "execution-special"


def test_normalizer_preserves_action() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            action=TaskAction.VERIFY,
        )
    )

    assert result.action is TaskAction.VERIFY


def test_normalizer_preserves_confidence() -> None:
    result = ExperienceNormalizer().normalize(make_experience(confidence=0.75))

    assert result.decision_confidence == 0.75


def test_confidence_is_normalized_to_float() -> None:
    result = NormalizedDecisionExperience(
        context_id=uuid4(),
        correlation_id=uuid4(),
        execution_id="execution-001",
        action=TaskAction.SUMMARIZE,
        decision_confidence=1,
        feedback_signals=(),
        effectiveness_status=EffectivenessStatus.UNKNOWN,
        effectiveness_dimensions=(),
    )

    assert result.decision_confidence == 1.0
    assert isinstance(result.decision_confidence, float)


def test_normalizer_preserves_effectiveness_status() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            status=EffectivenessStatus.DEGRADED,
        )
    )

    assert result.effectiveness_status is EffectivenessStatus.DEGRADED


def test_feedback_signals_are_sorted_canonically() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            signals=(
                FeedbackSignal.SUCCESS,
                FeedbackSignal.FALLBACK_USED,
                FeedbackSignal.PERFORMANCE_DEGRADED,
            )
        )
    )

    assert result.feedback_signals == tuple(
        sorted(
            result.feedback_signals,
            key=lambda signal: signal.value,
        )
    )


def test_signal_normalization_is_independent_of_input_order() -> None:
    first = make_experience(
        signals=(
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
            FeedbackSignal.FALLBACK_USED,
        )
    )

    second = make_experience(
        signals=(
            FeedbackSignal.FALLBACK_USED,
            FeedbackSignal.SUCCESS,
            FeedbackSignal.RETRY_OBSERVED,
        )
    )

    normalizer = ExperienceNormalizer()

    first_result = normalizer.normalize(first)
    second_result = normalizer.normalize(second)

    assert first_result.feedback_signals == second_result.feedback_signals


def test_dimensions_are_sorted_canonically() -> None:
    dimensions = {
        EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
        EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        EffectivenessDimension.PERFORMANCE: EffectivenessStatus.DEGRADED,
    }

    result = ExperienceNormalizer().normalize(
        make_experience(
            dimensions=dimensions,
        )
    )

    assert result.effectiveness_dimensions == tuple(
        sorted(
            dimensions.items(),
            key=lambda item: item[0].value,
        )
    )


def test_dimension_normalization_is_independent_of_mapping_order() -> None:
    first = make_experience(
        dimensions={
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
        }
    )

    second = make_experience(
        dimensions={
            EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        }
    )

    normalizer = ExperienceNormalizer()

    assert (
        normalizer.normalize(first).effectiveness_dimensions
        == normalizer.normalize(second).effectiveness_dimensions
    )


def test_comparison_key_contains_only_semantic_features() -> None:
    result = ExperienceNormalizer().normalize(make_experience())

    assert result.comparison_key == (
        result.action,
        result.decision_confidence,
        result.feedback_signals,
        result.effectiveness_status,
        result.effectiveness_dimensions,
    )


def test_context_id_is_excluded_from_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(make_experience(context_id=uuid4()))

    second = ExperienceNormalizer().normalize(make_experience(context_id=uuid4()))

    assert first.context_id != second.context_id
    assert first.comparison_key == second.comparison_key


def test_correlation_id_is_excluded_from_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(make_experience(correlation_id=uuid4()))

    second = ExperienceNormalizer().normalize(make_experience(correlation_id=uuid4()))

    assert first.correlation_id != second.correlation_id
    assert first.comparison_key == second.comparison_key


def test_execution_id_is_excluded_from_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(execution_id="execution-A")
    )

    second = ExperienceNormalizer().normalize(
        make_experience(execution_id="execution-B")
    )

    assert first.execution_id != second.execution_id
    assert first.comparison_key == second.comparison_key


def test_decision_reason_is_excluded_from_normalized_contract() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            reason="arbitrary high-cardinality reason",
        )
    )

    assert not hasattr(result, "decision_reason")


def test_effectiveness_reasons_are_excluded_from_normalized_contract() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            reasons=("arbitrary explanation",),
        )
    )

    assert not hasattr(result, "reasons")


def test_metadata_is_excluded_from_normalized_contract() -> None:
    result = ExperienceNormalizer().normalize(
        make_experience(
            metadata={
                "provider": "arbitrary",
                "request": "high-cardinality",
            }
        )
    )

    assert not hasattr(result, "metadata")


def test_different_free_form_reasons_have_same_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(
            reason="first reason",
            reasons=("first explanation",),
        )
    )

    second = ExperienceNormalizer().normalize(
        make_experience(
            reason="completely different reason",
            reasons=("different explanation",),
        )
    )

    assert first.comparison_key == second.comparison_key


def test_different_metadata_has_same_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(
            metadata={"source": "A"},
        )
    )

    second = ExperienceNormalizer().normalize(
        make_experience(
            metadata={"source": "B"},
        )
    )

    assert first.comparison_key == second.comparison_key


def test_different_action_changes_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(
            action=TaskAction.SUMMARIZE,
        )
    )

    second = ExperienceNormalizer().normalize(
        make_experience(
            action=TaskAction.VERIFY,
        )
    )

    assert first.comparison_key != second.comparison_key


def test_different_confidence_changes_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(make_experience(confidence=0.7))

    second = ExperienceNormalizer().normalize(make_experience(confidence=0.8))

    assert first.comparison_key != second.comparison_key


def test_different_feedback_changes_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(
            signals=(FeedbackSignal.SUCCESS,),
        )
    )

    second = ExperienceNormalizer().normalize(
        make_experience(
            signals=(
                FeedbackSignal.SUCCESS,
                FeedbackSignal.RETRY_OBSERVED,
            ),
        )
    )

    assert first.comparison_key != second.comparison_key


def test_different_effectiveness_status_changes_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(
            status=EffectivenessStatus.EFFECTIVE,
        )
    )

    second = ExperienceNormalizer().normalize(
        make_experience(
            status=EffectivenessStatus.DEGRADED,
        )
    )

    assert first.comparison_key != second.comparison_key


def test_different_dimension_changes_comparison_key() -> None:
    first = ExperienceNormalizer().normalize(
        make_experience(
            dimensions={
                EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
            }
        )
    )

    second = ExperienceNormalizer().normalize(
        make_experience(
            dimensions={
                EffectivenessDimension.OUTCOME: EffectivenessStatus.DEGRADED,
            }
        )
    )

    assert first.comparison_key != second.comparison_key


def test_normalizer_is_deterministic() -> None:
    experience = make_experience(
        signals=(
            FeedbackSignal.RETRY_OBSERVED,
            FeedbackSignal.SUCCESS,
        ),
        dimensions={
            EffectivenessDimension.RELIABILITY: EffectivenessStatus.DEGRADED,
            EffectivenessDimension.OUTCOME: EffectivenessStatus.EFFECTIVE,
        },
    )

    normalizer = ExperienceNormalizer()

    first = normalizer.normalize(experience)
    second = normalizer.normalize(experience)

    assert first == second
    assert first.comparison_key == second.comparison_key


def test_normalizer_does_not_modify_input() -> None:
    experience = make_experience()
    before = experience

    ExperienceNormalizer().normalize(experience)

    assert experience == before


def test_invalid_experience_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="experience must be a DecisionExperience",
    ):
        ExperienceNormalizer().normalize("invalid")


def test_normalized_contract_is_frozen() -> None:
    result = ExperienceNormalizer().normalize(make_experience())

    with pytest.raises(FrozenInstanceError):
        result.action = TaskAction.VERIFY


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        NormalizedDecisionExperience(
            context_id="invalid",
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions=(),
        )


def test_execution_id_must_not_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="execution_id must not be empty",
    ):
        NormalizedDecisionExperience(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="",
            action=TaskAction.SUMMARIZE,
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions=(),
        )


def test_invalid_confidence_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="decision_confidence must be between 0 and 1",
    ):
        NormalizedDecisionExperience(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_confidence=1.1,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.UNKNOWN,
            effectiveness_dimensions=(),
        )


def test_duplicate_signals_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="feedback_signals must not contain duplicates",
    ):
        NormalizedDecisionExperience(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_confidence=1.0,
            feedback_signals=(
                FeedbackSignal.SUCCESS,
                FeedbackSignal.SUCCESS,
            ),
            effectiveness_status=EffectivenessStatus.EFFECTIVE,
            effectiveness_dimensions=(),
        )


def test_duplicate_dimensions_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="must not contain duplicate dimensions",
    ):
        NormalizedDecisionExperience(
            context_id=uuid4(),
            correlation_id=uuid4(),
            execution_id="execution-001",
            action=TaskAction.SUMMARIZE,
            decision_confidence=1.0,
            feedback_signals=(),
            effectiveness_status=EffectivenessStatus.EFFECTIVE,
            effectiveness_dimensions=(
                (
                    EffectivenessDimension.OUTCOME,
                    EffectivenessStatus.EFFECTIVE,
                ),
                (
                    EffectivenessDimension.OUTCOME,
                    EffectivenessStatus.DEGRADED,
                ),
            ),
        )


def test_normalized_contract_contains_no_free_form_fields() -> None:
    forbidden = {
        "decision_reason",
        "reasons",
        "metadata",
        "provider",
        "source_text",
        "output",
        "runtime",
    }

    assert not (forbidden & set(NormalizedDecisionExperience.__dataclass_fields__))


def test_normalizer_has_no_storage_or_learning_interface() -> None:
    forbidden = {
        "save",
        "persist",
        "store",
        "search",
        "retrieve",
        "learn",
        "adapt",
        "replan",
        "execute",
    }

    public_names = {
        name for name in dir(ExperienceNormalizer) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_normalizer_exposes_only_normalize() -> None:
    public_names = {
        name for name in dir(ExperienceNormalizer) if not name.startswith("_")
    }

    assert public_names == {"normalize"}
