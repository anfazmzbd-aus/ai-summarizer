"""Tests for V10 adaptive policy composition boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationEligibilityEvaluator,
    AdaptationEligibilityStatus,
    AdaptationExplanationBuilder,
    AdaptationDisposition,
    AdaptiveIntelligencePolicy,
    AdaptivePolicyCompositionBoundary,
    AdaptivePolicyOutcome,
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

    explanation = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    return (
        informed,
        eligibility,
        adaptation,
        explanation,
    )


def compose_outcome(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> AdaptivePolicyOutcome:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain(
        disposition=disposition,
        action=action,
    )

    return AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )


def test_boundary_returns_adaptive_policy_outcome() -> None:
    result = compose_outcome()

    assert isinstance(result, AdaptivePolicyOutcome)


def test_context_id_is_preserved() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    result = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert result.context_id == informed.decision.context_id


def test_correlation_id_is_preserved() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    result = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert result.correlation_id == informed.decision.correlation_id


def test_action_is_preserved() -> None:
    result = compose_outcome(
        action=TaskAction.VERIFY,
    )

    assert result.action is TaskAction.VERIFY


def test_informed_decision_is_preserved() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    result = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert result.informed_decision is informed


def test_eligibility_is_preserved() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    result = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert result.eligibility is eligibility


def test_adaptation_decision_is_preserved() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    result = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert result.adaptation_decision is adaptation


def test_explanation_is_preserved() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    result = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert result.explanation is explanation


@pytest.mark.parametrize(
    "policy_disposition,eligibility_status,"
    "adaptation_disposition,historical_influence,"
    "adaptation_applied",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            AdaptationEligibilityStatus.INELIGIBLE,
            AdaptationDisposition.PRESERVE,
            False,
            False,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            AdaptationEligibilityStatus.ELIGIBLE,
            AdaptationDisposition.ADVISORY,
            True,
            True,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            AdaptationEligibilityStatus.ELIGIBLE,
            AdaptationDisposition.CONSTRAIN,
            True,
            True,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            AdaptationEligibilityStatus.REVIEW_ONLY,
            AdaptationDisposition.REVIEW,
            True,
            True,
        ),
    ],
)
def test_complete_m6_mapping_is_preserved(
    policy_disposition: DecisionSupportDisposition,
    eligibility_status: AdaptationEligibilityStatus,
    adaptation_disposition: AdaptationDisposition,
    historical_influence: bool,
    adaptation_applied: bool,
) -> None:
    result = compose_outcome(
        disposition=policy_disposition,
    )

    assert result.policy_disposition is policy_disposition
    assert result.eligibility_status is eligibility_status
    assert result.adaptation_disposition is adaptation_disposition
    assert result.historical_influence_applied is historical_influence
    assert result.adaptation_applied is adaptation_applied


def test_invalid_informed_decision_is_rejected() -> None:
    (
        _,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("informed_decision must be an " "ExperienceInformedDecision"),
    ):
        AdaptivePolicyCompositionBoundary().compose(
            "invalid",
            eligibility,
            adaptation,
            explanation,
        )


def test_invalid_eligibility_is_rejected() -> None:
    (
        informed,
        _,
        adaptation,
        explanation,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match="eligibility must be an AdaptationEligibility",
    ):
        AdaptivePolicyCompositionBoundary().compose(
            informed,
            "invalid",
            adaptation,
            explanation,
        )


def test_invalid_adaptation_decision_is_rejected() -> None:
    (
        informed,
        eligibility,
        _,
        explanation,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("adaptation_decision must be an AdaptationDecision"),
    ):
        AdaptivePolicyCompositionBoundary().compose(
            informed,
            eligibility,
            "invalid",
            explanation,
        )


def test_invalid_explanation_is_rejected() -> None:
    (
        informed,
        eligibility,
        adaptation,
        _,
    ) = make_chain()

    with pytest.raises(
        TypeError,
        match=("explanation must be an AdaptationExplanation"),
    ):
        AdaptivePolicyCompositionBoundary().compose(
            informed,
            eligibility,
            adaptation,
            "invalid",
        )


def test_outcome_rejects_context_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    with pytest.raises(
        ValueError,
        match=("context_id must match informed decision"),
    ):
        AdaptivePolicyOutcome(
            context_id=uuid4(),
            correlation_id=informed.decision.correlation_id,
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_correlation_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    with pytest.raises(
        ValueError,
        match=("correlation_id must match informed decision"),
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=uuid4(),
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_action_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    wrong_action = (
        TaskAction.VERIFY
        if informed.decision.action is TaskAction.SUMMARIZE
        else TaskAction.SUMMARIZE
    )

    with pytest.raises(
        ValueError,
        match="action must match informed decision",
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=informed.decision.correlation_id,
            action=wrong_action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_policy_disposition_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    with pytest.raises(
        ValueError,
        match=("policy_disposition must match informed decision"),
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=informed.decision.correlation_id,
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=DecisionSupportDisposition.CAUTION,
            eligibility_status=eligibility.status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_eligibility_status_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    wrong_status = (
        AdaptationEligibilityStatus.REVIEW_ONLY
        if eligibility.status is not AdaptationEligibilityStatus.REVIEW_ONLY
        else AdaptationEligibilityStatus.INELIGIBLE
    )

    with pytest.raises(
        ValueError,
        match="eligibility_status must match eligibility",
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=informed.decision.correlation_id,
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=wrong_status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_adaptation_disposition_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    wrong_disposition = (
        AdaptationDisposition.REVIEW
        if adaptation.disposition is not AdaptationDisposition.REVIEW
        else AdaptationDisposition.PRESERVE
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_disposition must match " "adaptation_decision"),
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=informed.decision.correlation_id,
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=wrong_disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_influence_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    with pytest.raises(
        ValueError,
        match=("historical_influence_applied must match " "informed_decision"),
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=informed.decision.correlation_id,
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(not informed.historical_influence_applied),
            adaptation_applied=adaptation.adaptation_applied,
        )


def test_outcome_rejects_adaptation_applied_mismatch() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    with pytest.raises(
        ValueError,
        match=("adaptation_applied must match adaptation_decision"),
    ):
        AdaptivePolicyOutcome(
            context_id=informed.decision.context_id,
            correlation_id=informed.decision.correlation_id,
            action=informed.decision.action,
            informed_decision=informed,
            eligibility=eligibility,
            adaptation_decision=adaptation,
            explanation=explanation,
            policy_disposition=(informed.policy_result.disposition),
            eligibility_status=eligibility.status,
            adaptation_disposition=adaptation.disposition,
            historical_influence_applied=(informed.historical_influence_applied),
            adaptation_applied=(not adaptation.adaptation_applied),
        )


def test_outcome_is_frozen() -> None:
    result = compose_outcome()

    with pytest.raises(FrozenInstanceError):
        result.adaptation_applied = False


def test_outcome_uses_slots() -> None:
    result = compose_outcome()

    assert not hasattr(result, "__dict__")


def test_boundary_is_deterministic() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    boundary = AdaptivePolicyCompositionBoundary()

    first = boundary.compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    second = boundary.compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert first == second


def test_boundary_does_not_modify_inputs() -> None:
    (
        informed,
        eligibility,
        adaptation,
        explanation,
    ) = make_chain()

    before = (
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    assert before == (
        informed,
        eligibility,
        adaptation,
        explanation,
    )


def test_outcome_contains_no_runtime_fields() -> None:
    forbidden = {
        "provider",
        "model",
        "strategy",
        "retry",
        "timeout",
        "runtime",
        "executor",
        "execution_graph",
        "prompt",
        "chunk_size",
        "streaming",
    }

    assert not (forbidden & set(AdaptivePolicyOutcome.__dataclass_fields__))


def test_boundary_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
    }

    public_names = {
        name
        for name in dir(AdaptivePolicyCompositionBoundary)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_boundary_exposes_only_compose() -> None:
    public_names = {
        name
        for name in dir(AdaptivePolicyCompositionBoundary)
        if not name.startswith("_")
    }

    assert public_names == {"compose"}
