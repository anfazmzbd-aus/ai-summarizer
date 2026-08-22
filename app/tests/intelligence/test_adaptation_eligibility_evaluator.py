"""Tests for V10 adaptation eligibility evaluation."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationEligibility,
    AdaptationEligibilityEvaluator,
    AdaptationEligibilityStatus,
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
    evidence_strength: EvidenceStrength = (EvidenceStrength.ESTABLISHED),
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
        evidence_strength=evidence_strength,
        disposition=disposition,
        reasons=("policy reason",),
    )


def make_informed_decision(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    evidence_strength: EvidenceStrength = (EvidenceStrength.ESTABLISHED),
) -> ExperienceInformedDecision:
    decision = make_decision()

    policy = make_policy_result(
        decision,
        disposition=disposition,
        evidence_strength=evidence_strength,
    )

    return ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )


def test_evaluator_returns_adaptation_eligibility() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(make_informed_decision())

    assert isinstance(
        result,
        AdaptationEligibility,
    )


def test_preserve_is_ineligible() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert result.status is AdaptationEligibilityStatus.INELIGIBLE


def test_advisory_is_eligible() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.ADVISORY,
        )
    )

    assert result.status is AdaptationEligibilityStatus.ELIGIBLE


def test_caution_is_eligible() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.CAUTION,
        )
    )

    assert result.status is AdaptationEligibilityStatus.ELIGIBLE


def test_review_is_review_only() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.REVIEW,
        )
    )

    assert result.status is AdaptationEligibilityStatus.REVIEW_ONLY


def test_non_established_evidence_is_ineligible() -> None:
    decision = make_decision()

    policy = DecisionSupportPolicyResult(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=decision.action,
        support_status=DecisionSupportStatus.SUPPORTED,
        evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
        evidence_strength=EvidenceStrength.LIMITED,
        disposition=DecisionSupportDisposition.ADVISORY,
        historical_influence_allowed=True,
        reasons=("test",),
    )

    informed = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.status is AdaptationEligibilityStatus.INELIGIBLE


def test_no_historical_influence_is_ineligible() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert result.historical_influence_applied is False
    assert result.status is AdaptationEligibilityStatus.INELIGIBLE


def test_evaluator_preserves_context_id() -> None:
    informed = make_informed_decision()

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.context_id == informed.decision.context_id


def test_evaluator_preserves_correlation_id() -> None:
    informed = make_informed_decision()

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.correlation_id == informed.decision.correlation_id


def test_evaluator_preserves_action() -> None:
    decision = make_decision(
        action=TaskAction.VERIFY,
    )

    policy = make_policy_result(
        decision,
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    informed = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "disposition",
    list(DecisionSupportDisposition),
)
def test_evaluator_preserves_policy_disposition(
    disposition: DecisionSupportDisposition,
) -> None:
    informed = make_informed_decision(
        disposition=disposition,
    )

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.policy_disposition is disposition


def test_evaluator_preserves_historical_influence() -> None:
    informed = make_informed_decision(
        disposition=DecisionSupportDisposition.ADVISORY,
    )

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.historical_influence_applied is informed.historical_influence_applied


def test_upstream_reasons_are_preserved() -> None:
    informed = make_informed_decision()

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert result.reasons[: len(informed.reasons)] == (informed.reasons)


def test_preserve_reason_is_added() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert any(
        "adaptation is ineligible" in reason or "adaptation is not permitted" in reason
        for reason in result.reasons
    )


def test_non_established_reason_is_added() -> None:
    decision = make_decision()

    policy = DecisionSupportPolicyResult(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=decision.action,
        support_status=DecisionSupportStatus.SUPPORTED,
        evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
        evidence_strength=EvidenceStrength.LIMITED,
        disposition=DecisionSupportDisposition.ADVISORY,
        historical_influence_allowed=True,
        reasons=("policy reason",),
    )

    informed = ExperienceInformedDecisionBoundary().compose(
        decision,
        policy,
    )

    result = AdaptationEligibilityEvaluator().evaluate(informed)

    assert any("not established enough" in reason for reason in result.reasons)


def test_eligible_reason_is_added() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.ADVISORY,
        )
    )

    assert any(
        "eligible for adaptive policy evaluation" in reason for reason in result.reasons
    )


def test_review_only_reason_is_added() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(
        make_informed_decision(
            disposition=DecisionSupportDisposition.REVIEW,
        )
    )

    assert any("review-only" in reason for reason in result.reasons)


def test_evaluator_rejects_invalid_input() -> None:
    with pytest.raises(
        TypeError,
        match=("informed_decision must be an " "ExperienceInformedDecision"),
    ):
        AdaptationEligibilityEvaluator().evaluate("invalid")


def test_evaluator_is_deterministic() -> None:
    informed = make_informed_decision(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    evaluator = AdaptationEligibilityEvaluator()

    first = evaluator.evaluate(informed)
    second = evaluator.evaluate(informed)

    assert first == second


def test_evaluator_does_not_modify_input() -> None:
    informed = make_informed_decision()

    before = informed

    AdaptationEligibilityEvaluator().evaluate(informed)

    assert informed == before


def test_eligibility_contains_no_runtime_action() -> None:
    result = AdaptationEligibilityEvaluator().evaluate(make_informed_decision())

    forbidden = {
        "provider",
        "model",
        "strategy",
        "retry",
        "timeout",
        "executor",
        "runtime",
        "replacement_action",
    }

    assert not (forbidden & set(result.__dataclass_fields__))


def test_evaluator_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "adapt",
        "select_strategy",
        "switch_provider",
        "apply_runtime",
    }

    public_names = {
        name for name in dir(AdaptationEligibilityEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_exposes_only_evaluate() -> None:
    public_names = {
        name for name in dir(AdaptationEligibilityEvaluator) if not name.startswith("_")
    }

    assert public_names == {"evaluate"}
