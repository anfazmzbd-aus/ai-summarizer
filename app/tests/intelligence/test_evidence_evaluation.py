"""Tests for V10 deterministic experience evidence evaluation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    EvidenceAssessment,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceEvidence,
    ExperienceEvidenceEvaluator,
    TaskAction,
)


def make_evidence(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
    effective: int = 0,
    degraded: int = 0,
    ineffective: int = 0,
    unknown: int = 0,
) -> ExperienceEvidence:
    sample_count = effective + degraded + ineffective + unknown

    return ExperienceEvidence.create(
        action=action,
        sample_count=sample_count,
        effective_count=effective,
        degraded_count=degraded,
        ineffective_count=ineffective,
        unknown_count=unknown,
    )


def test_assessment_status_values_are_stable() -> None:
    assert EvidenceAssessmentStatus.NO_EVIDENCE.value == "no_evidence"
    assert EvidenceAssessmentStatus.INSUFFICIENT.value == "insufficient"
    assert EvidenceAssessmentStatus.MIXED.value == "mixed"
    assert EvidenceAssessmentStatus.SUPPORTIVE.value == "supportive"
    assert EvidenceAssessmentStatus.CAUTIONARY.value == "cautionary"
    assert EvidenceAssessmentStatus.ADVERSE.value == "adverse"


def test_no_samples_produce_no_evidence() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence())

    assert result.status is EvidenceAssessmentStatus.NO_EVIDENCE


def test_one_sample_is_insufficient() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(effective=1))

    assert result.status is EvidenceAssessmentStatus.INSUFFICIENT


def test_two_samples_are_insufficient() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(effective=2))

    assert result.status is EvidenceAssessmentStatus.INSUFFICIENT


def test_three_effective_samples_are_supportive() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(effective=3))

    assert result.status is EvidenceAssessmentStatus.SUPPORTIVE


def test_effective_majority_is_supportive() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=4,
            degraded=1,
            ineffective=1,
        )
    )

    assert result.status is EvidenceAssessmentStatus.SUPPORTIVE


def test_ineffective_dominance_is_adverse() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=1,
            degraded=1,
            ineffective=3,
        )
    )

    assert result.status is EvidenceAssessmentStatus.ADVERSE


def test_all_ineffective_is_adverse() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            ineffective=3,
        )
    )

    assert result.status is EvidenceAssessmentStatus.ADVERSE


def test_negative_combination_is_cautionary() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=2,
            degraded=2,
            ineffective=1,
        )
    )

    assert result.status is EvidenceAssessmentStatus.CAUTIONARY


def test_degraded_majority_is_cautionary() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=1,
            degraded=3,
            ineffective=0,
        )
    )

    assert result.status is EvidenceAssessmentStatus.CAUTIONARY


def test_balanced_known_outcomes_are_mixed() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=2,
            degraded=1,
            ineffective=1,
        )
    )

    assert result.status is EvidenceAssessmentStatus.MIXED


def test_unknown_samples_do_not_vote_positive_or_negative() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=3,
            unknown=5,
        )
    )

    assert result.status is EvidenceAssessmentStatus.SUPPORTIVE
    assert result.known_count == 3
    assert result.unknown_count == 5


def test_established_samples_with_too_few_known_are_insufficient() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=1,
            unknown=4,
        )
    )

    assert result.evidence_strength is EvidenceStrength.ESTABLISHED
    assert result.known_count == 1
    assert result.status is EvidenceAssessmentStatus.INSUFFICIENT


def test_all_unknown_established_evidence_is_insufficient() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            unknown=5,
        )
    )

    assert result.known_count == 0
    assert result.status is EvidenceAssessmentStatus.INSUFFICIENT


def test_evaluator_preserves_action() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            action=TaskAction.VERIFY,
            effective=3,
        )
    )

    assert result.action is TaskAction.VERIFY


def test_evaluator_preserves_evidence_strength() -> None:
    evidence = make_evidence(
        effective=3,
    )

    result = ExperienceEvidenceEvaluator().evaluate(evidence)

    assert result.evidence_strength is evidence.strength


def test_sample_count_is_preserved() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=2,
            degraded=1,
            unknown=2,
        )
    )

    assert result.sample_count == 5


def test_known_count_is_derived() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=2,
            degraded=1,
            ineffective=1,
            unknown=3,
        )
    )

    assert result.known_count == 4


def test_unknown_count_is_preserved() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=3,
            unknown=2,
        )
    )

    assert result.unknown_count == 2


def test_no_evidence_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence())

    assert "no historical experience is available" in result.reasons


def test_limited_sample_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(effective=2))

    assert "historical sample size is limited" in result.reasons


def test_too_few_known_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=1,
            unknown=4,
        )
    )

    assert "too few historical outcomes are known" in result.reasons


def test_supportive_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(effective=3))

    assert any(
        "effective historical outcomes exceed" in reason for reason in result.reasons
    )


def test_adverse_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(ineffective=3))

    assert any(
        "ineffective historical outcomes exceed" in reason for reason in result.reasons
    )


def test_cautionary_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=1,
            degraded=2,
        )
    )

    assert any(
        "degraded and ineffective historical outcomes" in reason
        for reason in result.reasons
    )


def test_mixed_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=2,
            degraded=1,
            ineffective=1,
        )
    )

    assert "historical outcomes provide mixed evidence" in result.reasons


def test_unknown_count_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=3,
            unknown=2,
        )
    )

    assert "2 historical outcomes are unknown" in result.reasons


def test_known_count_reason_is_generated() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(
        make_evidence(
            effective=3,
        )
    )

    assert "3 historical outcomes are known" in result.reasons


def test_evaluator_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be an ExperienceEvidence",
    ):
        ExperienceEvidenceEvaluator().evaluate("invalid")


def test_assessment_action_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        EvidenceAssessment(
            action="summarize",
            evidence_strength=EvidenceStrength.NONE,
            status=EvidenceAssessmentStatus.NO_EVIDENCE,
            sample_count=0,
            known_count=0,
            unknown_count=0,
            reasons=(),
        )


def test_assessment_strength_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("evidence_strength must be an EvidenceStrength"),
    ):
        EvidenceAssessment(
            action=TaskAction.SUMMARIZE,
            evidence_strength="none",
            status=EvidenceAssessmentStatus.NO_EVIDENCE,
            sample_count=0,
            known_count=0,
            unknown_count=0,
            reasons=(),
        )


def test_assessment_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("status must be an EvidenceAssessmentStatus"),
    ):
        EvidenceAssessment(
            action=TaskAction.SUMMARIZE,
            evidence_strength=EvidenceStrength.NONE,
            status="no_evidence",
            sample_count=0,
            known_count=0,
            unknown_count=0,
            reasons=(),
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "known_count",
        "unknown_count",
    ],
)
def test_assessment_counts_must_be_integers(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "evidence_strength": EvidenceStrength.NONE,
        "status": EvidenceAssessmentStatus.NO_EVIDENCE,
        "sample_count": 0,
        "known_count": 0,
        "unknown_count": 0,
        "reasons": (),
    }

    values[field_name] = 1.5

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        EvidenceAssessment(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "sample_count",
        "known_count",
        "unknown_count",
    ],
)
def test_assessment_counts_reject_boolean(
    field_name: str,
) -> None:
    values = {
        "action": TaskAction.SUMMARIZE,
        "evidence_strength": EvidenceStrength.NONE,
        "status": EvidenceAssessmentStatus.NO_EVIDENCE,
        "sample_count": 0,
        "known_count": 0,
        "unknown_count": 0,
        "reasons": (),
    }

    values[field_name] = True

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an integer",
    ):
        EvidenceAssessment(**values)


def test_known_and_unknown_must_sum_to_sample_count() -> None:
    with pytest.raises(
        ValueError,
        match=("known_count and unknown_count " "must sum to sample_count"),
    ):
        EvidenceAssessment(
            action=TaskAction.SUMMARIZE,
            evidence_strength=EvidenceStrength.ESTABLISHED,
            status=EvidenceAssessmentStatus.SUPPORTIVE,
            sample_count=5,
            known_count=3,
            unknown_count=1,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        EvidenceAssessment(
            action=TaskAction.SUMMARIZE,
            evidence_strength=EvidenceStrength.NONE,
            status=EvidenceAssessmentStatus.NO_EVIDENCE,
            sample_count=0,
            known_count=0,
            unknown_count=0,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        EvidenceAssessment(
            action=TaskAction.SUMMARIZE,
            evidence_strength=EvidenceStrength.NONE,
            status=EvidenceAssessmentStatus.NO_EVIDENCE,
            sample_count=0,
            known_count=0,
            unknown_count=0,
            reasons=(123,),
        )


def test_assessment_is_frozen() -> None:
    result = ExperienceEvidenceEvaluator().evaluate(make_evidence(effective=3))

    with pytest.raises(FrozenInstanceError):
        result.status = EvidenceAssessmentStatus.ADVERSE


def test_evaluation_is_deterministic() -> None:
    evidence = make_evidence(
        effective=4,
        degraded=1,
        ineffective=1,
        unknown=2,
    )

    evaluator = ExperienceEvidenceEvaluator()

    first = evaluator.evaluate(evidence)
    second = evaluator.evaluate(evidence)

    assert first == second


def test_evaluator_does_not_modify_evidence() -> None:
    evidence = make_evidence(
        effective=3,
        degraded=1,
    )

    before = evidence

    ExperienceEvidenceEvaluator().evaluate(evidence)

    assert evidence == before


def test_assessment_contains_no_recommendation_fields() -> None:
    forbidden = {
        "recommendation",
        "recommended_action",
        "retry",
        "replan",
        "strategy",
        "provider",
        "policy",
        "decision",
        "reward",
    }

    assert not (forbidden & set(EvidenceAssessment.__dataclass_fields__))


def test_evaluator_has_no_decision_or_policy_interface() -> None:
    forbidden = {
        "recommend",
        "decide",
        "adapt",
        "apply_policy",
        "replan",
        "retry",
        "execute",
        "select_strategy",
        "switch_provider",
    }

    public_names = {
        name for name in dir(ExperienceEvidenceEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_exposes_only_evaluate() -> None:
    public_names = {
        name for name in dir(ExperienceEvidenceEvaluator) if not name.startswith("_")
    }

    assert public_names == {"evaluate"}
