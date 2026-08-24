"""Tests for V10 M7 orchestration translation policy."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationEligibilityEvaluator,
    AdaptationDisposition,
    AdaptationExplanationBuilder,
    AdaptiveIntelligencePolicy,
    AdaptivePolicyCompositionBoundary,
    AdaptivePolicyOutcome,
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceInformedDecisionBoundary,
    OrchestrationDirective,
    OrchestrationDisposition,
    OrchestrationTranslationPolicy,
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


def make_outcome(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> AdaptivePolicyOutcome:
    decision = make_decision(
        action=action,
    )

    policy_result = make_policy_result(
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

    return AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )


def test_translation_returns_orchestration_directive() -> None:
    result = OrchestrationTranslationPolicy().translate(make_outcome())

    assert isinstance(
        result,
        OrchestrationDirective,
    )


@pytest.mark.parametrize(
    "policy_disposition,expected_adaptation," "expected_orchestration",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            AdaptationDisposition.PRESERVE,
            OrchestrationDisposition.NO_CHANGE,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            AdaptationDisposition.ADVISORY,
            OrchestrationDisposition.ADVISORY_CONTEXT,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            AdaptationDisposition.CONSTRAIN,
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            AdaptationDisposition.REVIEW,
            OrchestrationDisposition.REVIEW_REQUIRED,
        ),
    ],
)
def test_complete_translation_matrix(
    policy_disposition: DecisionSupportDisposition,
    expected_adaptation: AdaptationDisposition,
    expected_orchestration: OrchestrationDisposition,
) -> None:
    outcome = make_outcome(
        disposition=policy_disposition,
    )

    result = OrchestrationTranslationPolicy().translate(outcome)

    assert result.adaptation_disposition is expected_adaptation

    assert result.orchestration_disposition is expected_orchestration


def test_no_change_disallows_execution_change() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert result.execution_change_allowed is False
    assert result.review_required is False


def test_advisory_context_disallows_execution_change() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.ADVISORY,
        )
    )

    assert result.execution_change_allowed is False
    assert result.review_required is False


def test_bounded_constraint_allows_execution_change() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.CAUTION,
        )
    )

    assert result.execution_change_allowed is True
    assert result.review_required is False


def test_review_required_does_not_allow_execution_change() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.REVIEW,
        )
    )

    assert result.execution_change_allowed is False
    assert result.review_required is True


def test_translation_preserves_context_id() -> None:
    outcome = make_outcome()

    result = OrchestrationTranslationPolicy().translate(outcome)

    assert result.context_id == outcome.context_id


def test_translation_preserves_correlation_id() -> None:
    outcome = make_outcome()

    result = OrchestrationTranslationPolicy().translate(outcome)

    assert result.correlation_id == outcome.correlation_id


def test_translation_preserves_action() -> None:
    outcome = make_outcome(
        action=TaskAction.VERIFY,
    )

    result = OrchestrationTranslationPolicy().translate(outcome)

    assert result.action is TaskAction.VERIFY


def test_translation_preserves_adaptation_disposition() -> None:
    outcome = make_outcome(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    result = OrchestrationTranslationPolicy().translate(outcome)

    assert result.adaptation_disposition is outcome.adaptation_disposition


def test_upstream_adaptation_reasons_are_preserved() -> None:
    outcome = make_outcome()

    result = OrchestrationTranslationPolicy().translate(outcome)

    upstream = outcome.adaptation_decision.reasons

    assert result.reasons[: len(upstream)] == upstream


def test_no_change_reason_is_added() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert any(
        "preserves existing execution behavior" in reason for reason in result.reasons
    )


def test_advisory_reason_is_added() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.ADVISORY,
        )
    )

    assert any(
        "without changing execution behavior" in reason for reason in result.reasons
    )


def test_constraint_reason_is_added() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.CAUTION,
        )
    )

    assert any("approved bounded constraints" in reason for reason in result.reasons)


def test_review_reason_is_added() -> None:
    result = OrchestrationTranslationPolicy().translate(
        make_outcome(
            disposition=DecisionSupportDisposition.REVIEW,
        )
    )

    assert any("review-oriented handling" in reason for reason in result.reasons)


def test_invalid_outcome_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="outcome must be an AdaptivePolicyOutcome",
    ):
        OrchestrationTranslationPolicy().translate("invalid")


def test_translation_is_deterministic() -> None:
    outcome = make_outcome(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    translator = OrchestrationTranslationPolicy()

    first = translator.translate(outcome)
    second = translator.translate(outcome)

    assert first == second


def test_translation_does_not_modify_outcome() -> None:
    outcome = make_outcome()

    before = outcome

    OrchestrationTranslationPolicy().translate(outcome)

    assert outcome == before


def test_translation_result_contains_no_runtime_fields() -> None:
    result = OrchestrationTranslationPolicy().translate(make_outcome())

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

    assert not (forbidden & set(result.__dataclass_fields__))


def test_translation_policy_has_no_runtime_interface() -> None:
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
        name for name in dir(OrchestrationTranslationPolicy) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_translation_policy_exposes_only_translate() -> None:
    public_names = {
        name for name in dir(OrchestrationTranslationPolicy) if not name.startswith("_")
    }

    assert public_names == {"translate"}
