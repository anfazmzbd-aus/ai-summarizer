"""Tests for the V10 experience evidence contract."""

from __future__ import annotations
from uuid import uuid4
from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    EvidenceStrength,
    ExperienceEvidence,
    ExperienceEvidenceBuilder,
    ExperienceLearningContext,
    TaskAction,
    EffectivenessDimension,
    EffectivenessStatus,
    FeedbackSignal,
    NormalizedDecisionExperience,
)


def make_context(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
    effective: int = 0,
    degraded: int = 0,
    ineffective: int = 0,
    unknown: int = 0,
) -> ExperienceLearningContext:

    experiences = []

    statuses = (
        [EffectivenessStatus.EFFECTIVE] * effective
        + [EffectivenessStatus.DEGRADED] * degraded
        + [EffectivenessStatus.INEFFECTIVE] * ineffective
        + [EffectivenessStatus.UNKNOWN] * unknown
    )

    for index, status in enumerate(statuses):
        experiences.append(
            NormalizedDecisionExperience(
                context_id=uuid4(),
                correlation_id=uuid4(),
                execution_id=f"execution-{index}",
                action=action,
                decision_confidence=0.8,
                feedback_signals=(FeedbackSignal.SUCCESS,),
                effectiveness_status=status,
                effectiveness_dimensions=(
                    (
                        EffectivenessDimension.OUTCOME,
                        status,
                    ),
                ),
            )
        )

    return ExperienceLearningContext(
        action=action,
        experiences=tuple(experiences),
        total_count=len(experiences),
        effective_count=effective,
        degraded_count=degraded,
        ineffective_count=ineffective,
        unknown_count=unknown,
    )


def make_evidence(
    *,
    sample_count: int = 0,
    effective: int = 0,
    degraded: int = 0,
    ineffective: int = 0,
    unknown: int = 0,
) -> ExperienceEvidence:
    return ExperienceEvidence.create(
        action=TaskAction.SUMMARIZE,
        sample_count=sample_count,
        effective_count=effective,
        degraded_count=degraded,
        ineffective_count=ineffective,
        unknown_count=unknown,
    )


def test_evidence_strength_values_are_stable() -> None:
    assert EvidenceStrength.NONE.value == "none"
    assert EvidenceStrength.LIMITED.value == "limited"
    assert EvidenceStrength.ESTABLISHED.value == "established"


def test_zero_samples_produce_no_evidence() -> None:
    result = make_evidence()

    assert result.strength is EvidenceStrength.NONE


def test_one_sample_produces_limited_evidence() -> None:
    result = make_evidence(
        sample_count=1,
        effective=1,
    )

    assert result.strength is EvidenceStrength.LIMITED


def test_two_samples_produce_limited_evidence() -> None:
    result = make_evidence(
        sample_count=2,
        effective=2,
    )

    assert result.strength is EvidenceStrength.LIMITED


def test_three_samples_produce_established_evidence() -> None:
    result = make_evidence(
        sample_count=3,
        effective=3,
    )

    assert result.strength is EvidenceStrength.ESTABLISHED


def test_larger_sample_produces_established_evidence() -> None:
    result = make_evidence(
        sample_count=10,
        effective=7,
        degraded=2,
        ineffective=1,
    )

    assert result.strength is EvidenceStrength.ESTABLISHED


def test_valid_evidence_preserves_counts() -> None:
    result = make_evidence(
        sample_count=4,
        effective=1,
        degraded=1,
        ineffective=1,
        unknown=1,
    )

    assert result.sample_count == 4
    assert result.effective_count == 1
    assert result.degraded_count == 1
    assert result.ineffective_count == 1
    assert result.unknown_count == 1


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        ExperienceEvidence(
            action="summarize",
            sample_count=0,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
            strength=EvidenceStrength.NONE,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "effective_count",
        "degraded_count",
        "ineffective_count",
        "unknown_count",
    ],
)
def test_counts_must_be_integers(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "sample_count": 0,
        "effective_count": 0,
        "degraded_count": 0,
        "ineffective_count": 0,
        "unknown_count": 0,
        "strength": EvidenceStrength.NONE,
    }

    values[field_name] = 1.5

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        ExperienceEvidence(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "effective_count",
        "degraded_count",
        "ineffective_count",
        "unknown_count",
    ],
)
def test_counts_reject_boolean(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "sample_count": 0,
        "effective_count": 0,
        "degraded_count": 0,
        "ineffective_count": 0,
        "unknown_count": 0,
        "strength": EvidenceStrength.NONE,
    }

    values[field_name] = True

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        ExperienceEvidence(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "effective_count",
        "degraded_count",
        "ineffective_count",
        "unknown_count",
    ],
)
def test_counts_must_be_non_negative(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "sample_count": 0,
        "effective_count": 0,
        "degraded_count": 0,
        "ineffective_count": 0,
        "unknown_count": 0,
        "strength": EvidenceStrength.NONE,
    }

    values[field_name] = -1

    with pytest.raises(
        ValueError,
        match=(f"{field_name} must be greater than or equal to 0"),
    ):
        ExperienceEvidence(**values)


def test_counts_must_sum_to_sample_count() -> None:
    with pytest.raises(
        ValueError,
        match=("effectiveness counts must sum to sample_count"),
    ):
        ExperienceEvidence(
            action=TaskAction.SUMMARIZE,
            sample_count=2,
            effective_count=1,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
            strength=EvidenceStrength.LIMITED,
        )


def test_strength_must_be_evidence_strength() -> None:
    with pytest.raises(
        TypeError,
        match="strength must be an EvidenceStrength",
    ):
        ExperienceEvidence(
            action=TaskAction.SUMMARIZE,
            sample_count=0,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
            strength="none",
        )


def test_strength_must_match_sample_count() -> None:
    with pytest.raises(
        ValueError,
        match="strength must match sample_count",
    ):
        ExperienceEvidence(
            action=TaskAction.SUMMARIZE,
            sample_count=3,
            effective_count=3,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
            strength=EvidenceStrength.LIMITED,
        )


def test_factory_derives_strength() -> None:
    result = ExperienceEvidence.create(
        action=TaskAction.SUMMARIZE,
        sample_count=3,
        effective_count=2,
        degraded_count=1,
        ineffective_count=0,
        unknown_count=0,
    )

    assert result.strength is EvidenceStrength.ESTABLISHED


def test_factory_rejects_invalid_sample_count_type() -> None:
    with pytest.raises(
        TypeError,
        match="sample_count must be an integer",
    ):
        ExperienceEvidence.create(
            action=TaskAction.SUMMARIZE,
            sample_count=1.5,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_factory_rejects_negative_sample_count() -> None:
    with pytest.raises(
        ValueError,
        match=("sample_count must be greater than or equal to 0"),
    ):
        ExperienceEvidence.create(
            action=TaskAction.SUMMARIZE,
            sample_count=-1,
            effective_count=0,
            degraded_count=0,
            ineffective_count=0,
            unknown_count=0,
        )


def test_evidence_is_frozen() -> None:
    result = make_evidence()

    with pytest.raises(FrozenInstanceError):
        result.sample_count = 1


def test_builder_returns_experience_evidence() -> None:
    context = make_context()

    result = ExperienceEvidenceBuilder().build(context)

    assert isinstance(result, ExperienceEvidence)


def test_builder_preserves_action() -> None:
    context = make_context(
        action=TaskAction.VERIFY,
    )

    result = ExperienceEvidenceBuilder().build(context)

    assert result.action is TaskAction.VERIFY


def test_builder_preserves_distribution() -> None:
    context = make_context(
        effective=3,
        degraded=2,
        ineffective=1,
        unknown=1,
    )

    result = ExperienceEvidenceBuilder().build(context)

    assert result.sample_count == 7
    assert result.effective_count == 3
    assert result.degraded_count == 2
    assert result.ineffective_count == 1
    assert result.unknown_count == 1


def test_builder_derives_no_strength() -> None:
    context = make_context()

    result = ExperienceEvidenceBuilder().build(context)

    assert result.strength is EvidenceStrength.NONE


def test_builder_derives_limited_strength() -> None:
    context = make_context(
        effective=2,
    )

    result = ExperienceEvidenceBuilder().build(context)

    assert result.strength is EvidenceStrength.LIMITED


def test_builder_derives_established_strength() -> None:
    context = make_context(
        effective=3,
    )

    result = ExperienceEvidenceBuilder().build(context)

    assert result.strength is EvidenceStrength.ESTABLISHED


def test_builder_rejects_invalid_context() -> None:
    with pytest.raises(
        TypeError,
        match=("context must be an ExperienceLearningContext"),
    ):
        ExperienceEvidenceBuilder().build("invalid")


def test_builder_is_deterministic() -> None:
    context = make_context(
        effective=3,
        degraded=1,
        unknown=1,
    )

    builder = ExperienceEvidenceBuilder()

    first = builder.build(context)
    second = builder.build(context)

    assert first == second


def test_builder_does_not_modify_context() -> None:
    context = make_context(
        effective=3,
    )

    before = context

    ExperienceEvidenceBuilder().build(context)

    assert context == before


def test_evidence_contains_no_recommendation_fields() -> None:
    forbidden = {
        "recommended_action",
        "recommendation",
        "retry",
        "replan",
        "strategy",
        "provider",
        "policy",
        "reward",
        "penalty",
    }

    assert not (forbidden & set(ExperienceEvidence.__dataclass_fields__))


def test_builder_has_no_policy_or_adaptive_interface() -> None:
    forbidden = {
        "recommend",
        "adapt",
        "learn",
        "replan",
        "retry",
        "execute",
        "select_strategy",
        "switch_provider",
    }

    public_names = {
        name for name in dir(ExperienceEvidenceBuilder) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(ExperienceEvidenceBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
