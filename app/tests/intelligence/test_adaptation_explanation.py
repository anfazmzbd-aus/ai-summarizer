"""Tests for V10 adaptation explainability and provenance."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDecision,
    AdaptationEligibilityEvaluator,
    AdaptationEligibilityStatus,
    AdaptationExplanation,
    AdaptationExplanationBuilder,
    AdaptationDisposition,
    AdaptiveIntelligencePolicy,
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceInformedDecisionBoundary,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=action,
        reason="test decision",
        confidence=1.0,
    )


def make_policy(
    decision: TaskDecision,
    *,
    disposition: DecisionSupportDisposition,
) -> DecisionSupportPolicyResult:
    if disposition is DecisionSupportDisposition.PRESERVE:
        support_status = DecisionSupportStatus.NEUTRAL
        evidence_status = EvidenceAssessmentStatus.MIXED

    elif disposition is DecisionSupportDisposition.ADVISORY:
        support_status = DecisionSupportStatus.SUPPORTED
        evidence_status = EvidenceAssessmentStatus.SUPPORTIVE

    elif disposition is DecisionSupportDisposition.CAUTION:
        support_status = DecisionSupportStatus.CAUTION
        evidence_status = EvidenceAssessmentStatus.CAUTIONARY

    else:
        support_status = DecisionSupportStatus.UNSUPPORTED
        evidence_status = EvidenceAssessmentStatus.ADVERSE

    return DecisionSupportPolicyResult.create(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=decision.action,
        support_status=support_status,
        evidence_status=evidence_status,
        evidence_strength=EvidenceStrength.ESTABLISHED,
        disposition=disposition,
        reasons=("policy reason",),
    )


def make_chain(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
):
    decision = make_decision(
        action=action,
    )

    policy_result = make_policy(
        decision,
        disposition=disposition,
    )

    informed = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy_result,
    )

    eligibility = AdaptationEligibilityEvaluator().evaluate(informed)

    adaptation = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    return (
        decision,
        informed,
        eligibility,
        adaptation,
    )


def build_explanation(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> AdaptationExplanation:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain(
        disposition=disposition,
        action=action,
    )

    return AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )


def test_builder_returns_adaptation_explanation() -> None:
    result = build_explanation()

    assert isinstance(
        result,
        AdaptationExplanation,
    )


def test_context_id_is_preserved() -> None:
    (
        decision,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    result = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    assert result.context_id == decision.context_id


def test_correlation_id_is_preserved() -> None:
    (
        decision,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    result = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    assert result.correlation_id == decision.correlation_id


def test_action_is_preserved() -> None:
    result = build_explanation(
        action=TaskAction.VERIFY,
    )

    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "policy_disposition,expected",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            AdaptationDisposition.PRESERVE,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            AdaptationDisposition.ADVISORY,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            AdaptationDisposition.CONSTRAIN,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            AdaptationDisposition.REVIEW,
        ),
    ],
)
def test_adaptation_disposition_is_explained(
    policy_disposition: DecisionSupportDisposition,
    expected: AdaptationDisposition,
) -> None:
    result = build_explanation(
        disposition=policy_disposition,
    )

    assert result.adaptation_disposition is expected


def test_preserve_is_ineligible_and_not_applied() -> None:
    result = build_explanation(
        disposition=DecisionSupportDisposition.PRESERVE,
    )

    assert result.eligibility_status is AdaptationEligibilityStatus.INELIGIBLE
    assert result.historical_influence_applied is False
    assert result.adaptation_applied is False


def test_advisory_is_eligible_and_applied() -> None:
    result = build_explanation(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    assert result.eligibility_status is AdaptationEligibilityStatus.ELIGIBLE
    assert result.historical_influence_applied is True
    assert result.adaptation_applied is True


def test_caution_is_eligible_and_applied() -> None:
    result = build_explanation(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    assert result.eligibility_status is AdaptationEligibilityStatus.ELIGIBLE
    assert result.adaptation_applied is True


def test_review_is_review_only_and_applied() -> None:
    result = build_explanation(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    assert result.eligibility_status is AdaptationEligibilityStatus.REVIEW_ONLY
    assert result.adaptation_applied is True


def test_informed_decision_reasons_are_preserved() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    result = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    assert result.informed_decision_reasons == informed.reasons


def test_eligibility_reasons_are_preserved() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    result = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    assert result.eligibility_reasons == eligibility.reasons


def test_adaptation_reasons_are_preserved() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    result = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    assert result.adaptation_reasons == adaptation.reasons


def test_builder_rejects_invalid_informed_decision() -> None:
    (
        _,
        _,
        eligibility,
        adaptation,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("informed_decision must be an " "ExperienceInformedDecision"),
    ):
        AdaptationExplanationBuilder().build(
            "invalid",
            eligibility,
            adaptation,
        )


def test_builder_rejects_invalid_eligibility() -> None:
    (
        _,
        informed,
        _,
        adaptation,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("eligibility must be an AdaptationEligibility"),
    ):
        AdaptationExplanationBuilder().build(
            informed,
            "invalid",
            adaptation,
        )


def test_builder_rejects_invalid_adaptation_decision() -> None:
    (
        _,
        informed,
        eligibility,
        _,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("adaptation_decision must be an " "AdaptationDecision"),
    ):
        AdaptationExplanationBuilder().build(
            informed,
            eligibility,
            "invalid",
        )


def test_context_mismatch_is_rejected() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    invalid = AdaptationDecision.create(
        context_id=uuid4(),
        correlation_id=adaptation.correlation_id,
        action=adaptation.action,
        eligibility_status=adaptation.eligibility_status,
        disposition=adaptation.disposition,
        reasons=adaptation.reasons,
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_decision context_id must match " "eligibility"),
    ):
        AdaptationExplanationBuilder().build(
            informed,
            eligibility,
            invalid,
        )


def test_correlation_mismatch_is_rejected() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    invalid = AdaptationDecision.create(
        context_id=adaptation.context_id,
        correlation_id=uuid4(),
        action=adaptation.action,
        eligibility_status=adaptation.eligibility_status,
        disposition=adaptation.disposition,
        reasons=adaptation.reasons,
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_decision correlation_id must match " "eligibility"),
    ):
        AdaptationExplanationBuilder().build(
            informed,
            eligibility,
            invalid,
        )


def test_action_mismatch_is_rejected() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    invalid = AdaptationDecision.create(
        context_id=adaptation.context_id,
        correlation_id=adaptation.correlation_id,
        action=TaskAction.VERIFY,
        eligibility_status=adaptation.eligibility_status,
        disposition=adaptation.disposition,
        reasons=adaptation.reasons,
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_decision action must match eligibility"),
    ):
        AdaptationExplanationBuilder().build(
            informed,
            eligibility,
            invalid,
        )


def test_eligibility_status_mismatch_is_rejected() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    invalid = AdaptationDecision.create(
        context_id=adaptation.context_id,
        correlation_id=adaptation.correlation_id,
        action=adaptation.action,
        eligibility_status=(AdaptationEligibilityStatus.REVIEW_ONLY),
        disposition=adaptation.disposition,
        reasons=adaptation.reasons,
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_decision eligibility_status must " "match eligibility"),
    ):
        AdaptationExplanationBuilder().build(
            informed,
            eligibility,
            invalid,
        )


def test_explanation_is_frozen() -> None:
    result = build_explanation()

    with pytest.raises(FrozenInstanceError):
        result.adaptation_applied = False


def test_explanation_uses_slots() -> None:
    result = build_explanation()

    assert not hasattr(result, "__dict__")


def test_builder_is_deterministic() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    builder = AdaptationExplanationBuilder()

    first = builder.build(
        informed,
        eligibility,
        adaptation,
    )

    second = builder.build(
        informed,
        eligibility,
        adaptation,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    (
        _,
        informed,
        eligibility,
        adaptation,
    ) = make_chain()

    before = (
        informed,
        eligibility,
        adaptation,
    )

    AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    assert before == (
        informed,
        eligibility,
        adaptation,
    )


def test_explanation_contains_no_runtime_fields() -> None:
    forbidden = {
        "provider",
        "model",
        "strategy",
        "retry",
        "timeout",
        "runtime",
        "executor",
        "prompt",
        "replacement_action",
    }

    assert not (forbidden & set(AdaptationExplanation.__dataclass_fields__))


def test_builder_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "adapt",
        "apply_runtime",
        "switch_provider",
        "select_strategy",
    }

    public_names = {
        name for name in dir(AdaptationExplanationBuilder) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(AdaptationExplanationBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
