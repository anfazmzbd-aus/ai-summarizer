"""Tests for V10 adaptive intelligence policy."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDecision,
    AdaptationDisposition,
    AdaptationEligibility,
    AdaptationEligibilityStatus,
    AdaptiveIntelligencePolicy,
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceInformedDecision,
    ExperienceInformedDecisionBoundary,
    TaskAction,
    TaskDecision,
)


def make_decision(
    *,
    context_id=None,
    correlation_id=None,
    action: TaskAction = TaskAction.SUMMARIZE,
) -> TaskDecision:
    return TaskDecision.create(
        context_id=context_id or uuid4(),
        correlation_id=correlation_id or uuid4(),
        action=action,
        reason="test decision",
        confidence=1.0,
    )


def make_policy_result(
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


def make_informed(
    *,
    disposition: DecisionSupportDisposition,
    action: TaskAction = TaskAction.SUMMARIZE,
) -> ExperienceInformedDecision:
    decision = make_decision(
        action=action,
    )

    policy = make_policy_result(
        decision,
        disposition=disposition,
    )

    return ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )


def make_eligibility(
    informed: ExperienceInformedDecision,
    *,
    status: AdaptationEligibilityStatus,
) -> AdaptationEligibility:
    return AdaptationEligibility.create(
        context_id=informed.decision.context_id,
        correlation_id=informed.decision.correlation_id,
        action=informed.decision.action,
        policy_disposition=(informed.policy_result.disposition),
        historical_influence_applied=(informed.historical_influence_applied),
        status=status,
        reasons=("eligibility reason",),
    )


def test_policy_returns_adaptation_decision() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert isinstance(result, AdaptationDecision)


def test_ineligible_forces_preserve() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.INELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.disposition is AdaptationDisposition.PRESERVE


def test_review_only_forces_review() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.REVIEW_ONLY,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.disposition is AdaptationDisposition.REVIEW


def test_eligible_advisory_maps_to_advisory() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.disposition is AdaptationDisposition.ADVISORY


def test_eligible_caution_maps_to_constrain() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.disposition is AdaptationDisposition.CONSTRAIN


def test_eligible_review_maps_to_review() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.disposition is AdaptationDisposition.REVIEW


def test_eligible_preserve_maps_to_preserve() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.PRESERVE,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.disposition is AdaptationDisposition.PRESERVE


def test_preserve_does_not_apply_adaptation() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.PRESERVE,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.INELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.adaptation_applied is False


def test_advisory_applies_adaptation() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.adaptation_applied is True


def test_constrain_applies_adaptation() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.adaptation_applied is True


def test_review_applies_adaptation() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.REVIEW_ONLY,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.adaptation_applied is True


def test_policy_preserves_context_id() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.context_id == informed.decision.context_id


def test_policy_preserves_correlation_id() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.correlation_id == informed.decision.correlation_id


def test_policy_preserves_action() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
        action=TaskAction.VERIFY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.action is TaskAction.VERIFY


def test_policy_preserves_eligibility_status() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.eligibility_status is AdaptationEligibilityStatus.ELIGIBLE


def test_eligibility_reasons_are_preserved() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = AdaptationEligibility.create(
        context_id=informed.decision.context_id,
        correlation_id=informed.decision.correlation_id,
        action=informed.decision.action,
        policy_disposition=(informed.policy_result.disposition),
        historical_influence_applied=(informed.historical_influence_applied),
        status=AdaptationEligibilityStatus.ELIGIBLE,
        reasons=("first", "second"),
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert result.reasons[:2] == ("first", "second")


def test_preserve_reason_is_added() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.PRESERVE,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.INELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert "adaptive policy preserves the original decision" in result.reasons


def test_advisory_reason_is_added() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert any("advisory historical context" in reason for reason in result.reasons)


def test_constrain_reason_is_added() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert any("constraint-oriented handling" in reason for reason in result.reasons)


def test_review_reason_is_added() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.REVIEW,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.REVIEW_ONLY,
    )

    result = AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert any("review-oriented handling" in reason for reason in result.reasons)


def test_policy_rejects_invalid_informed_decision() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    with pytest.raises(
        TypeError,
        match=("informed_decision must be an " "ExperienceInformedDecision"),
    ):
        AdaptiveIntelligencePolicy().apply(
            "invalid",
            eligibility,
        )


def test_policy_rejects_invalid_eligibility() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    with pytest.raises(
        TypeError,
        match=("eligibility must be an AdaptationEligibility"),
    ):
        AdaptiveIntelligencePolicy().apply(
            informed,
            "invalid",
        )


def test_context_mismatch_is_rejected() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = AdaptationEligibility.create(
        context_id=uuid4(),
        correlation_id=informed.decision.correlation_id,
        action=informed.decision.action,
        policy_disposition=(informed.policy_result.disposition),
        historical_influence_applied=(informed.historical_influence_applied),
        status=AdaptationEligibilityStatus.ELIGIBLE,
        reasons=(),
    )

    with pytest.raises(
        ValueError,
        match=("decision and eligibility context_id must match"),
    ):
        AdaptiveIntelligencePolicy().apply(
            informed,
            eligibility,
        )


def test_correlation_mismatch_is_rejected() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = AdaptationEligibility.create(
        context_id=informed.decision.context_id,
        correlation_id=uuid4(),
        action=informed.decision.action,
        policy_disposition=(informed.policy_result.disposition),
        historical_influence_applied=(informed.historical_influence_applied),
        status=AdaptationEligibilityStatus.ELIGIBLE,
        reasons=(),
    )

    with pytest.raises(
        ValueError,
        match=("decision and eligibility correlation_id must match"),
    ):
        AdaptiveIntelligencePolicy().apply(
            informed,
            eligibility,
        )


def test_action_mismatch_is_rejected() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = AdaptationEligibility.create(
        context_id=informed.decision.context_id,
        correlation_id=informed.decision.correlation_id,
        action=TaskAction.VERIFY,
        policy_disposition=(informed.policy_result.disposition),
        historical_influence_applied=(informed.historical_influence_applied),
        status=AdaptationEligibilityStatus.ELIGIBLE,
        reasons=(),
    )

    with pytest.raises(
        ValueError,
        match="decision and eligibility action must match",
    ):
        AdaptiveIntelligencePolicy().apply(
            informed,
            eligibility,
        )


def test_policy_disposition_mismatch_is_rejected() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = AdaptationEligibility.create(
        context_id=informed.decision.context_id,
        correlation_id=informed.decision.correlation_id,
        action=informed.decision.action,
        policy_disposition=DecisionSupportDisposition.CAUTION,
        historical_influence_applied=(informed.historical_influence_applied),
        status=AdaptationEligibilityStatus.ELIGIBLE,
        reasons=(),
    )

    with pytest.raises(
        ValueError,
        match="policy disposition must match eligibility",
    ):
        AdaptiveIntelligencePolicy().apply(
            informed,
            eligibility,
        )


def test_historical_influence_mismatch_is_rejected() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = AdaptationEligibility.create(
        context_id=informed.decision.context_id,
        correlation_id=informed.decision.correlation_id,
        action=informed.decision.action,
        policy_disposition=(informed.policy_result.disposition),
        historical_influence_applied=False,
        status=AdaptationEligibilityStatus.ELIGIBLE,
        reasons=(),
    )

    with pytest.raises(
        ValueError,
        match="historical influence must match eligibility",
    ):
        AdaptiveIntelligencePolicy().apply(
            informed,
            eligibility,
        )


def test_policy_is_deterministic() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    policy = AdaptiveIntelligencePolicy()

    first = policy.apply(
        informed,
        eligibility,
    )

    second = policy.apply(
        informed,
        eligibility,
    )

    assert first == second


def test_policy_does_not_modify_inputs() -> None:
    informed = make_informed(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    eligibility = make_eligibility(
        informed,
        status=AdaptationEligibilityStatus.ELIGIBLE,
    )

    informed_before = informed
    eligibility_before = eligibility

    AdaptiveIntelligencePolicy().apply(
        informed,
        eligibility,
    )

    assert informed == informed_before
    assert eligibility == eligibility_before


def test_policy_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
        "apply_runtime",
    }

    public_names = {
        name for name in dir(AdaptiveIntelligencePolicy) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_policy_exposes_only_apply() -> None:
    public_names = {
        name for name in dir(AdaptiveIntelligencePolicy) if not name.startswith("_")
    }

    assert public_names == {"apply"}
