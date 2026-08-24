"""Tests for V10 M8 intelligence trace builder and provenance validation."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDisposition,
    AdaptationEligibilityStatus,
    AdaptationExplanation,
    DecisionExplanation,
    DecisionSupportDisposition,
    DecisionSupportStatus,
    DirectiveValidationStatus,
    EvidenceAssessmentStatus,
    EvidenceStrength,
    ExecutionIntegrationMode,
    IntegrationExplanation,
    IntelligenceTrace,
    IntelligenceTraceBuilder,
    OrchestrationDisposition,
    TaskAction,
)


def make_decision_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
    historical_influence_applied: bool = True,
) -> DecisionExplanation:
    return DecisionExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        sample_count=3,
        effective_count=3,
        degraded_count=0,
        ineffective_count=0,
        unknown_count=0,
        evidence_strength=EvidenceStrength.ESTABLISHED,
        evidence_status=EvidenceAssessmentStatus.SUPPORTIVE,
        support_status=DecisionSupportStatus.SUPPORTED,
        disposition=DecisionSupportDisposition.ADVISORY,
        historical_influence_applied=(historical_influence_applied),
        evidence_reasons=("evidence",),
        support_reasons=("support",),
        policy_reasons=("policy",),
        decision_reasons=("decision",),
    )


def make_adaptation_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
    historical_influence_applied: bool = True,
    adaptation_applied: bool = True,
) -> AdaptationExplanation:
    return AdaptationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        policy_disposition=DecisionSupportDisposition.ADVISORY,
        eligibility_status=AdaptationEligibilityStatus.ELIGIBLE,
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        historical_influence_applied=(historical_influence_applied),
        adaptation_applied=adaptation_applied,
        informed_decision_reasons=("decision",),
        eligibility_reasons=("eligibility",),
        adaptation_reasons=("adaptation",),
    )


def make_integration_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
    execution_authorized: bool = False,
    review_required: bool = False,
) -> IntegrationExplanation:
    return IntegrationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        validation_status=DirectiveValidationStatus.VALID,
        integration_mode=ExecutionIntegrationMode.ADVISORY,
        execution_authorized=execution_authorized,
        bounded_constraint_required=False,
        review_required=review_required,
        orchestration_reasons=("orchestration",),
        validation_reasons=("validation",),
        integration_reasons=("integration",),
    )


def make_chain(
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
    historical_influence_applied: bool = True,
    adaptation_applied: bool = True,
    execution_authorized: bool = False,
    review_required: bool = False,
):
    context_id = uuid4()
    correlation_id = uuid4()

    decision = make_decision_explanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        historical_influence_applied=(historical_influence_applied),
    )

    adaptation = make_adaptation_explanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        historical_influence_applied=(historical_influence_applied),
        adaptation_applied=adaptation_applied,
    )

    integration = make_integration_explanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        execution_authorized=execution_authorized,
        review_required=review_required,
    )

    return decision, adaptation, integration


def test_builder_returns_intelligence_trace() -> None:
    decision, adaptation, integration = make_chain()

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert isinstance(result, IntelligenceTrace)


def test_builder_preserves_explanation_objects() -> None:
    decision, adaptation, integration = make_chain()

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert result.decision_explanation is decision
    assert result.adaptation_explanation is adaptation
    assert result.integration_explanation is integration


def test_builder_preserves_provenance() -> None:
    decision, adaptation, integration = make_chain(
        action=TaskAction.VERIFY,
    )

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert result.context_id == decision.context_id
    assert result.correlation_id == decision.correlation_id
    assert result.action is TaskAction.VERIFY


def test_historical_influence_is_derived_from_adaptation() -> None:
    decision, adaptation, integration = make_chain(
        historical_influence_applied=False,
        adaptation_applied=False,
    )

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert result.historical_influence_applied is False


def test_adaptation_applied_is_derived_from_adaptation() -> None:
    decision, adaptation, integration = make_chain(
        adaptation_applied=False,
    )

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert result.adaptation_applied is False


def test_execution_authorized_is_derived_from_integration() -> None:
    decision, adaptation, integration = make_chain(
        execution_authorized=True,
    )

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert result.execution_authorized is True


def test_review_required_is_derived_from_integration() -> None:
    decision, adaptation, integration = make_chain(
        review_required=True,
    )

    result = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert result.review_required is True


def test_invalid_decision_explanation_is_rejected() -> None:
    _, adaptation, integration = make_chain()

    with pytest.raises(
        TypeError,
        match=("decision_explanation must be a DecisionExplanation"),
    ):
        IntelligenceTraceBuilder().build(
            "invalid",
            adaptation,
            integration,
        )


def test_invalid_adaptation_explanation_is_rejected() -> None:
    decision, _, integration = make_chain()

    with pytest.raises(
        TypeError,
        match=("adaptation_explanation must be an " "AdaptationExplanation"),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            "invalid",
            integration,
        )


def test_invalid_integration_explanation_is_rejected() -> None:
    decision, adaptation, _ = make_chain()

    with pytest.raises(
        TypeError,
        match=("integration_explanation must be an " "IntegrationExplanation"),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            "invalid",
        )


def test_adaptation_context_mismatch_is_rejected() -> None:
    decision, _, integration = make_chain()

    adaptation = make_adaptation_explanation(
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
        action=decision.action,
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_explanation context_id must match " "decision_explanation"),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_integration_context_mismatch_is_rejected() -> None:
    decision, adaptation, _ = make_chain()

    integration = make_integration_explanation(
        context_id=uuid4(),
        correlation_id=decision.correlation_id,
        action=decision.action,
    )

    with pytest.raises(
        ValueError,
        match=("integration_explanation context_id must match " "decision_explanation"),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_adaptation_correlation_mismatch_is_rejected() -> None:
    decision, _, integration = make_chain()

    adaptation = make_adaptation_explanation(
        context_id=decision.context_id,
        correlation_id=uuid4(),
        action=decision.action,
    )

    with pytest.raises(
        ValueError,
        match=(
            "adaptation_explanation correlation_id must match " "decision_explanation"
        ),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_integration_correlation_mismatch_is_rejected() -> None:
    decision, adaptation, _ = make_chain()

    integration = make_integration_explanation(
        context_id=decision.context_id,
        correlation_id=uuid4(),
        action=decision.action,
    )

    with pytest.raises(
        ValueError,
        match=(
            "integration_explanation correlation_id must match " "decision_explanation"
        ),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_adaptation_action_mismatch_is_rejected() -> None:
    decision, _, integration = make_chain()

    adaptation = make_adaptation_explanation(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=TaskAction.VERIFY,
    )

    with pytest.raises(
        ValueError,
        match=("adaptation_explanation action must match " "decision_explanation"),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_integration_action_mismatch_is_rejected() -> None:
    decision, adaptation, _ = make_chain()

    integration = make_integration_explanation(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=TaskAction.VERIFY,
    )

    with pytest.raises(
        ValueError,
        match=("integration_explanation action must match " "decision_explanation"),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_historical_influence_mismatch_is_rejected() -> None:
    decision, _, integration = make_chain(
        historical_influence_applied=True,
    )

    adaptation = make_adaptation_explanation(
        context_id=decision.context_id,
        correlation_id=decision.correlation_id,
        action=decision.action,
        historical_influence_applied=False,
        adaptation_applied=False,
    )

    with pytest.raises(
        ValueError,
        match=(
            "historical influence must match across "
            "decision and adaptation explanations"
        ),
    ):
        IntelligenceTraceBuilder().build(
            decision,
            adaptation,
            integration,
        )


def test_builder_is_deterministic() -> None:
    decision, adaptation, integration = make_chain()

    builder = IntelligenceTraceBuilder()

    first = builder.build(
        decision,
        adaptation,
        integration,
    )

    second = builder.build(
        decision,
        adaptation,
        integration,
    )

    assert first == second


def test_builder_does_not_modify_inputs() -> None:
    decision, adaptation, integration = make_chain()

    before = (
        decision,
        adaptation,
        integration,
    )

    IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    assert before == (
        decision,
        adaptation,
        integration,
    )


def test_builder_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "adapt",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
    }

    public_names = {
        name for name in dir(IntelligenceTraceBuilder) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(IntelligenceTraceBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
