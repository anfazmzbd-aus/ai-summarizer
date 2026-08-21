"""Tests for V10 decision explainability and provenance."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    BoundedDecisionSupportPolicy,
    DecisionExplanation,
    DecisionExplanationBuilder,
    DecisionSupportBuilder,
    DecisionSupportDisposition,
    EvidenceAssessmentStatus,
    ExperienceEvidence,
    ExperienceEvidenceEvaluator,
    ExperienceInformedDecisionBoundary,
    TaskAction,
    TaskDecision,
)


def make_chain(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
    effective: int = 3,
    degraded: int = 0,
    ineffective: int = 0,
    unknown: int = 0,
):
    decision = TaskDecision.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=action,
        reason="test decision",
        confidence=1.0,
    )

    evidence = ExperienceEvidence.create(
        action=action,
        sample_count=(effective + degraded + ineffective + unknown),
        effective_count=effective,
        degraded_count=degraded,
        ineffective_count=ineffective,
        unknown_count=unknown,
    )

    assessment = ExperienceEvidenceEvaluator().evaluate(evidence)

    support = DecisionSupportBuilder().build(
        decision,
        assessment,
    )

    policy = BoundedDecisionSupportPolicy().apply(support)

    informed = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    return (
        decision,
        evidence,
        assessment,
        support,
        policy,
        informed,
    )


def build_explanation(**kwargs) -> DecisionExplanation:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain(**kwargs)

    return DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )


def test_builder_returns_decision_explanation() -> None:
    result = build_explanation()

    assert isinstance(result, DecisionExplanation)


def test_explanation_preserves_context_id() -> None:
    (
        decision,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    result = DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert result.context_id == decision.context_id


def test_explanation_preserves_correlation_id() -> None:
    (
        decision,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    result = DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert result.correlation_id == decision.correlation_id


def test_explanation_preserves_action() -> None:
    result = build_explanation(
        action=TaskAction.VERIFY,
    )

    assert result.action is TaskAction.VERIFY


def test_explanation_preserves_evidence_distribution() -> None:
    result = build_explanation(
        effective=4,
        degraded=2,
        ineffective=1,
        unknown=3,
    )

    assert result.sample_count == 10
    assert result.effective_count == 4
    assert result.degraded_count == 2
    assert result.ineffective_count == 1
    assert result.unknown_count == 3


def test_supportive_chain_is_explained() -> None:
    result = build_explanation(
        effective=4,
    )

    assert result.evidence_status is EvidenceAssessmentStatus.SUPPORTIVE
    assert result.disposition is DecisionSupportDisposition.ADVISORY
    assert result.historical_influence_applied is True


def test_adverse_chain_is_explained() -> None:
    result = build_explanation(
        ineffective=4,
        effective=0,
    )

    assert result.evidence_status is EvidenceAssessmentStatus.ADVERSE
    assert result.disposition is DecisionSupportDisposition.REVIEW
    assert result.historical_influence_applied is True


def test_no_evidence_chain_is_preserved() -> None:
    result = build_explanation(
        effective=0,
    )

    assert result.evidence_status is EvidenceAssessmentStatus.NO_EVIDENCE
    assert result.disposition is DecisionSupportDisposition.PRESERVE
    assert result.historical_influence_applied is False


def test_evidence_reasons_are_preserved() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    result = DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert result.evidence_reasons == assessment.reasons


def test_support_reasons_are_preserved() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    result = DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert result.support_reasons == support.reasons


def test_policy_reasons_are_preserved() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    result = DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert result.policy_reasons == policy.reasons


def test_decision_reasons_are_preserved() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    result = DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert result.decision_reasons == informed.reasons


def test_builder_rejects_invalid_evidence() -> None:
    (
        _,
        _,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match="evidence must be an ExperienceEvidence",
    ):
        DecisionExplanationBuilder().build(
            "invalid",
            assessment,
            support,
            policy,
            informed,
        )


def test_builder_rejects_invalid_assessment() -> None:
    (
        _,
        evidence,
        _,
        support,
        policy,
        informed,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match="assessment must be an EvidenceAssessment",
    ):
        DecisionExplanationBuilder().build(
            evidence,
            "invalid",
            support,
            policy,
            informed,
        )


def test_builder_rejects_invalid_support() -> None:
    (
        _,
        evidence,
        assessment,
        _,
        policy,
        informed,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match="support must be a DecisionSupportAssessment",
    ):
        DecisionExplanationBuilder().build(
            evidence,
            assessment,
            "invalid",
            policy,
            informed,
        )


def test_builder_rejects_invalid_policy_result() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        _,
        informed,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("policy_result must be a DecisionSupportPolicyResult"),
    ):
        DecisionExplanationBuilder().build(
            evidence,
            assessment,
            support,
            "invalid",
            informed,
        )


def test_builder_rejects_invalid_informed_decision() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        _,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("informed_decision must be an " "ExperienceInformedDecision"),
    ):
        DecisionExplanationBuilder().build(
            evidence,
            assessment,
            support,
            policy,
            "invalid",
        )


def test_action_mismatch_is_rejected() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    mismatched_evidence = ExperienceEvidence.create(
        action=TaskAction.VERIFY,
        sample_count=evidence.sample_count,
        effective_count=evidence.effective_count,
        degraded_count=evidence.degraded_count,
        ineffective_count=evidence.ineffective_count,
        unknown_count=evidence.unknown_count,
    )

    with pytest.raises(
        ValueError,
        match="all M5 chain actions must match",
    ):
        DecisionExplanationBuilder().build(
            mismatched_evidence,
            assessment,
            support,
            policy,
            informed,
        )


def test_sample_count_mismatch_is_rejected() -> None:
    (
        decision,
        evidence,
        _,
        support,
        policy,
        informed,
    ) = make_chain()

    other_evidence = ExperienceEvidence.create(
        action=decision.action,
        sample_count=4,
        effective_count=4,
        degraded_count=0,
        ineffective_count=0,
        unknown_count=0,
    )

    other_assessment = ExperienceEvidenceEvaluator().evaluate(other_evidence)

    with pytest.raises(
        ValueError,
        match="assessment sample_count must match evidence",
    ):
        DecisionExplanationBuilder().build(
            evidence,
            other_assessment,
            support,
            policy,
            informed,
        )


def test_support_evidence_status_mismatch_is_rejected() -> None:
    (
        decision,
        evidence,
        assessment,
        _,
        policy,
        informed,
    ) = make_chain()

    adverse_evidence = ExperienceEvidence.create(
        action=decision.action,
        sample_count=3,
        effective_count=0,
        degraded_count=0,
        ineffective_count=3,
        unknown_count=0,
    )

    adverse_assessment = ExperienceEvidenceEvaluator().evaluate(adverse_evidence)

    mismatched_support = DecisionSupportBuilder().build(
        decision,
        adverse_assessment,
    )

    with pytest.raises(
        ValueError,
        match=("support evidence_status must match assessment"),
    ):
        DecisionExplanationBuilder().build(
            evidence,
            assessment,
            mismatched_support,
            policy,
            informed,
        )


def test_policy_support_status_mismatch_is_rejected() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        _,
        informed,
    ) = make_chain()

    caution_support = DecisionSupportBuilder().build(
        informed.decision,
        ExperienceEvidenceEvaluator().evaluate(
            ExperienceEvidence.create(
                action=informed.decision.action,
                sample_count=3,
                effective_count=1,
                degraded_count=2,
                ineffective_count=0,
                unknown_count=0,
            )
        ),
    )

    caution_policy = BoundedDecisionSupportPolicy().apply(caution_support)

    with pytest.raises(
        ValueError,
        match=("policy_result support_status must match support"),
    ):
        DecisionExplanationBuilder().build(
            evidence,
            assessment,
            support,
            caution_policy,
            informed,
        )


def test_explanation_is_frozen() -> None:
    result = build_explanation()

    with pytest.raises(FrozenInstanceError):
        result.sample_count = 999


def test_builder_is_deterministic() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    builder = DecisionExplanationBuilder()

    first = builder.build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    second = builder.build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    (
        _,
        evidence,
        assessment,
        support,
        policy,
        informed,
    ) = make_chain()

    values_before = (
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    DecisionExplanationBuilder().build(
        evidence,
        assessment,
        support,
        policy,
        informed,
    )

    assert values_before == (
        evidence,
        assessment,
        support,
        policy,
        informed,
    )


def test_explanation_contains_no_runtime_action_fields() -> None:
    forbidden = {
        "replacement_action",
        "recommended_action",
        "new_decision",
        "retry",
        "replan",
        "provider",
        "strategy",
        "runtime",
        "executor",
    }

    assert not (forbidden & set(DecisionExplanation.__dataclass_fields__))


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(DecisionExplanationBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
