"""Tests for V10 M7 intelligence-to-orchestration handoff."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationEligibilityEvaluator,
    AdaptationExplanationBuilder,
    AdaptiveIntelligencePolicy,
    AdaptivePolicyCompositionBoundary,
    DecisionSupportDisposition,
    DecisionSupportPolicyResult,
    DecisionSupportStatus,
    DirectiveValidationStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExperienceInformedDecisionBoundary,
    IntelligenceOrchestrationHandoff,
    IntelligenceOrchestrationHandoffBoundary,
    OrchestrationDirectiveGuard,
    OrchestrationDisposition,
    OrchestrationTranslationPolicy,
    TaskAction,
    TaskDecision,
)


def make_policy_result(
    decision: TaskDecision,
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
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
):
    decision = TaskDecision.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=action,
        reason="test decision",
        confidence=1.0,
    )

    policy_result = make_policy_result(
        decision,
        disposition,
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

    outcome = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        explanation,
    )

    directive = OrchestrationTranslationPolicy().translate(outcome)

    validation = OrchestrationDirectiveGuard().validate(directive)

    return outcome, directive, validation


def make_handoff(
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> IntelligenceOrchestrationHandoff:
    outcome, directive, validation = make_chain(
        disposition,
        action,
    )

    return IntelligenceOrchestrationHandoffBoundary().compose(
        outcome,
        directive,
        validation,
    )


def test_boundary_returns_handoff() -> None:
    result = make_handoff()

    assert isinstance(
        result,
        IntelligenceOrchestrationHandoff,
    )


def test_provenance_is_preserved() -> None:
    outcome, directive, validation = make_chain(
        action=TaskAction.VERIFY,
    )

    result = IntelligenceOrchestrationHandoffBoundary().compose(
        outcome,
        directive,
        validation,
    )

    assert result.context_id == outcome.context_id
    assert result.correlation_id == outcome.correlation_id
    assert result.action is TaskAction.VERIFY


def test_chain_objects_are_preserved() -> None:
    outcome, directive, validation = make_chain()

    result = IntelligenceOrchestrationHandoffBoundary().compose(
        outcome,
        directive,
        validation,
    )

    assert result.adaptive_outcome is outcome
    assert result.directive is directive
    assert result.validation is validation


@pytest.mark.parametrize(
    "disposition,expected_orchestration," "expected_authorized,expected_review",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            OrchestrationDisposition.NO_CHANGE,
            False,
            False,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            OrchestrationDisposition.ADVISORY_CONTEXT,
            False,
            False,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            True,
            False,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            OrchestrationDisposition.REVIEW_REQUIRED,
            False,
            True,
        ),
    ],
)
def test_complete_handoff_matrix(
    disposition: DecisionSupportDisposition,
    expected_orchestration: OrchestrationDisposition,
    expected_authorized: bool,
    expected_review: bool,
) -> None:
    result = make_handoff(disposition)

    assert result.orchestration_disposition is expected_orchestration
    assert result.execution_authorized is expected_authorized
    assert result.review_required is expected_review


def test_handoff_requires_valid_validation() -> None:
    outcome, directive, validation = make_chain()

    rejected = type(validation)(
        directive=directive,
        status=DirectiveValidationStatus.REJECTED,
        execution_authorized=False,
        review_required=False,
        reasons=("rejected",),
    )

    with pytest.raises(
        ValueError,
        match="handoff requires a valid directive validation",
    ):
        IntelligenceOrchestrationHandoffBoundary().compose(
            outcome,
            directive,
            rejected,
        )


def test_context_mismatch_is_rejected() -> None:
    outcome, directive, validation = make_chain()

    with pytest.raises(
        ValueError,
        match="context_id must match adaptive_outcome",
    ):
        IntelligenceOrchestrationHandoff(
            context_id=uuid4(),
            correlation_id=outcome.correlation_id,
            action=outcome.action,
            adaptive_outcome=outcome,
            directive=directive,
            validation=validation,
            orchestration_disposition=(directive.orchestration_disposition),
            execution_authorized=(validation.execution_authorized),
            review_required=validation.review_required,
        )


def test_correlation_mismatch_is_rejected() -> None:
    outcome, directive, validation = make_chain()

    with pytest.raises(
        ValueError,
        match="correlation_id must match adaptive_outcome",
    ):
        IntelligenceOrchestrationHandoff(
            context_id=outcome.context_id,
            correlation_id=uuid4(),
            action=outcome.action,
            adaptive_outcome=outcome,
            directive=directive,
            validation=validation,
            orchestration_disposition=(directive.orchestration_disposition),
            execution_authorized=(validation.execution_authorized),
            review_required=validation.review_required,
        )


def test_action_mismatch_is_rejected() -> None:
    outcome, directive, validation = make_chain()

    wrong_action = (
        TaskAction.VERIFY
        if outcome.action is TaskAction.SUMMARIZE
        else TaskAction.SUMMARIZE
    )

    with pytest.raises(
        ValueError,
        match="action must match adaptive_outcome",
    ):
        IntelligenceOrchestrationHandoff(
            context_id=outcome.context_id,
            correlation_id=outcome.correlation_id,
            action=wrong_action,
            adaptive_outcome=outcome,
            directive=directive,
            validation=validation,
            orchestration_disposition=(directive.orchestration_disposition),
            execution_authorized=(validation.execution_authorized),
            review_required=validation.review_required,
        )


def test_invalid_adaptive_outcome_is_rejected() -> None:
    _, directive, validation = make_chain()

    with pytest.raises(
        TypeError,
        match=("adaptive_outcome must be an AdaptivePolicyOutcome"),
    ):
        IntelligenceOrchestrationHandoffBoundary().compose(
            "invalid",
            directive,
            validation,
        )


def test_invalid_directive_is_rejected() -> None:
    outcome, _, validation = make_chain()

    with pytest.raises(
        TypeError,
        match=("directive must be an OrchestrationDirective"),
    ):
        IntelligenceOrchestrationHandoffBoundary().compose(
            outcome,
            "invalid",
            validation,
        )


def test_invalid_validation_is_rejected() -> None:
    outcome, directive, _ = make_chain()

    with pytest.raises(
        TypeError,
        match=("validation must be an " "OrchestrationDirectiveValidation"),
    ):
        IntelligenceOrchestrationHandoffBoundary().compose(
            outcome,
            directive,
            "invalid",
        )


def test_handoff_is_frozen() -> None:
    result = make_handoff()

    with pytest.raises(FrozenInstanceError):
        result.execution_authorized = True


def test_handoff_uses_slots() -> None:
    result = make_handoff()

    assert not hasattr(result, "__dict__")


def test_boundary_is_deterministic() -> None:
    outcome, directive, validation = make_chain()

    boundary = IntelligenceOrchestrationHandoffBoundary()

    first = boundary.compose(
        outcome,
        directive,
        validation,
    )
    second = boundary.compose(
        outcome,
        directive,
        validation,
    )

    assert first == second


def test_boundary_does_not_modify_inputs() -> None:
    outcome, directive, validation = make_chain()

    before = outcome, directive, validation

    IntelligenceOrchestrationHandoffBoundary().compose(
        outcome,
        directive,
        validation,
    )

    assert before == (outcome, directive, validation)


def test_handoff_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntelligenceOrchestrationHandoff.__dataclass_fields__))


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
        for name in dir(IntelligenceOrchestrationHandoffBoundary)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_boundary_exposes_only_compose() -> None:
    public_names = {
        name
        for name in dir(IntelligenceOrchestrationHandoffBoundary)
        if not name.startswith("_")
    }

    assert public_names == {"compose"}
