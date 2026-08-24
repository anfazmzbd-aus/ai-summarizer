"""Tests for V10 M7 integration explainability and safety."""

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
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExecutionIntegrationMode,
    ExistingExecutionIntegrationAdapter,
    ExperienceInformedDecisionBoundary,
    IntegrationExplanation,
    IntegrationExplanationBuilder,
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
    *,
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

    adaptation_explanation = AdaptationExplanationBuilder().build(
        informed,
        eligibility,
        adaptation,
    )

    outcome = AdaptivePolicyCompositionBoundary().compose(
        informed,
        eligibility,
        adaptation,
        adaptation_explanation,
    )

    directive = OrchestrationTranslationPolicy().translate(outcome)

    validation = OrchestrationDirectiveGuard().validate(directive)

    handoff = IntelligenceOrchestrationHandoffBoundary().compose(
        outcome,
        directive,
        validation,
    )

    integration = ExistingExecutionIntegrationAdapter().adapt(handoff)

    return handoff, integration


def build_explanation(
    *,
    disposition: DecisionSupportDisposition = (DecisionSupportDisposition.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> IntegrationExplanation:
    handoff, integration = make_chain(
        disposition=disposition,
        action=action,
    )

    return IntegrationExplanationBuilder().build(
        handoff,
        integration,
    )


def test_builder_returns_integration_explanation() -> None:
    result = build_explanation()

    assert isinstance(
        result,
        IntegrationExplanation,
    )


def test_provenance_is_preserved() -> None:
    handoff, integration = make_chain(
        action=TaskAction.VERIFY,
    )

    result = IntegrationExplanationBuilder().build(
        handoff,
        integration,
    )

    assert result.context_id == handoff.context_id
    assert result.correlation_id == handoff.correlation_id
    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "disposition,expected_orchestration,"
    "expected_mode,expected_authorized,"
    "expected_constraint,expected_review",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            OrchestrationDisposition.NO_CHANGE,
            ExecutionIntegrationMode.PRESERVE,
            False,
            False,
            False,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            OrchestrationDisposition.ADVISORY_CONTEXT,
            ExecutionIntegrationMode.ADVISORY,
            False,
            False,
            False,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            ExecutionIntegrationMode.CONSTRAINED,
            True,
            True,
            False,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            OrchestrationDisposition.REVIEW_REQUIRED,
            ExecutionIntegrationMode.REVIEW,
            False,
            False,
            True,
        ),
    ],
)
def test_complete_integration_explanation_matrix(
    disposition: DecisionSupportDisposition,
    expected_orchestration: OrchestrationDisposition,
    expected_mode: ExecutionIntegrationMode,
    expected_authorized: bool,
    expected_constraint: bool,
    expected_review: bool,
) -> None:
    result = build_explanation(
        disposition=disposition,
    )

    assert result.orchestration_disposition is expected_orchestration
    assert result.integration_mode is expected_mode
    assert result.execution_authorized is expected_authorized
    assert result.bounded_constraint_required is expected_constraint
    assert result.review_required is expected_review


def test_orchestration_reasons_are_preserved() -> None:
    handoff, integration = make_chain()

    result = IntegrationExplanationBuilder().build(
        handoff,
        integration,
    )

    assert result.orchestration_reasons == handoff.directive.reasons


def test_validation_reasons_are_preserved() -> None:
    handoff, integration = make_chain()

    result = IntegrationExplanationBuilder().build(
        handoff,
        integration,
    )

    assert result.validation_reasons == handoff.validation.reasons


def test_integration_reasons_are_preserved() -> None:
    handoff, integration = make_chain()

    result = IntegrationExplanationBuilder().build(
        handoff,
        integration,
    )

    assert result.integration_reasons == integration.reasons


def test_invalid_handoff_is_rejected() -> None:
    _, integration = make_chain()

    with pytest.raises(
        TypeError,
        match=("handoff must be an " "IntelligenceOrchestrationHandoff"),
    ):
        IntegrationExplanationBuilder().build(
            "invalid",
            integration,
        )


def test_invalid_integration_is_rejected() -> None:
    handoff, _ = make_chain()

    with pytest.raises(
        TypeError,
        match=("integration must be an " "ExecutionIntegrationDirective"),
    ):
        IntegrationExplanationBuilder().build(
            handoff,
            "invalid",
        )


def test_context_mismatch_is_rejected() -> None:
    handoff, integration = make_chain()

    invalid = type(integration)(
        context_id=uuid4(),
        correlation_id=integration.correlation_id,
        action=integration.action,
        mode=integration.mode,
        preserve_existing_behavior=(integration.preserve_existing_behavior),
        execution_change_authorized=(integration.execution_change_authorized),
        bounded_constraint_required=(integration.bounded_constraint_required),
        review_required=integration.review_required,
        reasons=integration.reasons,
    )

    with pytest.raises(
        ValueError,
        match=("integration context_id must match handoff"),
    ):
        IntegrationExplanationBuilder().build(
            handoff,
            invalid,
        )


def test_correlation_mismatch_is_rejected() -> None:
    handoff, integration = make_chain()

    invalid = type(integration)(
        context_id=integration.context_id,
        correlation_id=uuid4(),
        action=integration.action,
        mode=integration.mode,
        preserve_existing_behavior=(integration.preserve_existing_behavior),
        execution_change_authorized=(integration.execution_change_authorized),
        bounded_constraint_required=(integration.bounded_constraint_required),
        review_required=integration.review_required,
        reasons=integration.reasons,
    )

    with pytest.raises(
        ValueError,
        match=("integration correlation_id must match handoff"),
    ):
        IntegrationExplanationBuilder().build(
            handoff,
            invalid,
        )


def test_action_mismatch_is_rejected() -> None:
    handoff, integration = make_chain()

    wrong_action = (
        TaskAction.VERIFY
        if integration.action is TaskAction.SUMMARIZE
        else TaskAction.SUMMARIZE
    )

    invalid = type(integration)(
        context_id=integration.context_id,
        correlation_id=integration.correlation_id,
        action=wrong_action,
        mode=integration.mode,
        preserve_existing_behavior=(integration.preserve_existing_behavior),
        execution_change_authorized=(integration.execution_change_authorized),
        bounded_constraint_required=(integration.bounded_constraint_required),
        review_required=integration.review_required,
        reasons=integration.reasons,
    )

    with pytest.raises(
        ValueError,
        match="integration action must match handoff",
    ):
        IntegrationExplanationBuilder().build(
            handoff,
            invalid,
        )


def test_explanation_is_frozen() -> None:
    result = build_explanation()

    with pytest.raises(FrozenInstanceError):
        result.review_required = True


def test_explanation_uses_slots() -> None:
    result = build_explanation()

    assert not hasattr(result, "__dict__")


def test_builder_is_deterministic() -> None:
    handoff, integration = make_chain(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    builder = IntegrationExplanationBuilder()

    first = builder.build(
        handoff,
        integration,
    )

    second = builder.build(
        handoff,
        integration,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    handoff, integration = make_chain()

    before = handoff, integration

    IntegrationExplanationBuilder().build(
        handoff,
        integration,
    )

    assert before == (handoff, integration)


def test_explanation_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntegrationExplanation.__dataclass_fields__))


def test_builder_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "run",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
    }

    public_names = {
        name for name in dir(IntegrationExplanationBuilder) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(IntegrationExplanationBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
