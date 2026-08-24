"""Tests for V10 M8 intelligence trace contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
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
    OrchestrationDisposition,
    TaskAction,
)


def make_decision_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
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
        historical_influence_applied=True,
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
) -> AdaptationExplanation:
    return AdaptationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        policy_disposition=DecisionSupportDisposition.ADVISORY,
        eligibility_status=AdaptationEligibilityStatus.ELIGIBLE,
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        historical_influence_applied=True,
        adaptation_applied=True,
        informed_decision_reasons=("decision",),
        eligibility_reasons=("eligibility",),
        adaptation_reasons=("adaptation",),
    )


def make_integration_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
) -> IntegrationExplanation:
    return IntegrationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        validation_status=DirectiveValidationStatus.VALID,
        integration_mode=ExecutionIntegrationMode.ADVISORY,
        execution_authorized=False,
        bounded_constraint_required=False,
        review_required=False,
        orchestration_reasons=("orchestration",),
        validation_reasons=("validation",),
        integration_reasons=("integration",),
    )


def make_trace() -> IntelligenceTrace:
    context_id = uuid4()
    correlation_id = uuid4()
    action = TaskAction.SUMMARIZE

    return IntelligenceTrace(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        decision_explanation=make_decision_explanation(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
        ),
        adaptation_explanation=make_adaptation_explanation(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
        ),
        integration_explanation=make_integration_explanation(
            context_id=context_id,
            correlation_id=correlation_id,
            action=action,
        ),
        historical_influence_applied=True,
        adaptation_applied=True,
        execution_authorized=False,
        review_required=False,
    )


def test_create_returns_intelligence_trace() -> None:
    result = make_trace()

    assert isinstance(result, IntelligenceTrace)


def test_context_id_is_preserved() -> None:
    result = make_trace()

    assert result.context_id == result.decision_explanation.context_id


def test_correlation_id_is_preserved() -> None:
    result = make_trace()

    assert result.correlation_id == result.decision_explanation.correlation_id


def test_action_is_preserved() -> None:
    result = make_trace()

    assert result.action is TaskAction.SUMMARIZE


def test_explanation_contracts_are_preserved() -> None:
    result = make_trace()

    assert isinstance(
        result.decision_explanation,
        DecisionExplanation,
    )
    assert isinstance(
        result.adaptation_explanation,
        AdaptationExplanation,
    )
    assert isinstance(
        result.integration_explanation,
        IntegrationExplanation,
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "historical_influence_applied",
        "adaptation_applied",
        "execution_authorized",
        "review_required",
    ],
)
def test_boolean_fields_are_preserved(
    field_name: str,
) -> None:
    result = make_trace()

    assert isinstance(
        getattr(result, field_name),
        bool,
    )


def test_context_id_must_be_uuid() -> None:
    trace = make_trace()

    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        IntelligenceTrace(
            context_id="invalid",
            correlation_id=trace.correlation_id,
            action=trace.action,
            decision_explanation=trace.decision_explanation,
            adaptation_explanation=trace.adaptation_explanation,
            integration_explanation=trace.integration_explanation,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
        )


def test_correlation_id_must_be_uuid() -> None:
    trace = make_trace()

    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        IntelligenceTrace(
            context_id=trace.context_id,
            correlation_id="invalid",
            action=trace.action,
            decision_explanation=trace.decision_explanation,
            adaptation_explanation=trace.adaptation_explanation,
            integration_explanation=trace.integration_explanation,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
        )


def test_action_must_be_task_action() -> None:
    trace = make_trace()

    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        IntelligenceTrace(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action="summarize",
            decision_explanation=trace.decision_explanation,
            adaptation_explanation=trace.adaptation_explanation,
            integration_explanation=trace.integration_explanation,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
        )


def test_decision_explanation_must_be_valid() -> None:
    trace = make_trace()

    with pytest.raises(
        TypeError,
        match=("decision_explanation must be a DecisionExplanation"),
    ):
        IntelligenceTrace(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            decision_explanation="invalid",
            adaptation_explanation=trace.adaptation_explanation,
            integration_explanation=trace.integration_explanation,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
        )


def test_adaptation_explanation_must_be_valid() -> None:
    trace = make_trace()

    with pytest.raises(
        TypeError,
        match=("adaptation_explanation must be an " "AdaptationExplanation"),
    ):
        IntelligenceTrace(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            decision_explanation=trace.decision_explanation,
            adaptation_explanation="invalid",
            integration_explanation=trace.integration_explanation,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
        )


def test_integration_explanation_must_be_valid() -> None:
    trace = make_trace()

    with pytest.raises(
        TypeError,
        match=("integration_explanation must be an " "IntegrationExplanation"),
    ):
        IntelligenceTrace(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            decision_explanation=trace.decision_explanation,
            adaptation_explanation=trace.adaptation_explanation,
            integration_explanation="invalid",
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "historical_influence_applied",
        "adaptation_applied",
        "execution_authorized",
        "review_required",
    ],
)
def test_boolean_fields_require_bool(
    field_name: str,
) -> None:
    trace = make_trace()

    values = {
        "context_id": trace.context_id,
        "correlation_id": trace.correlation_id,
        "action": trace.action,
        "decision_explanation": trace.decision_explanation,
        "adaptation_explanation": trace.adaptation_explanation,
        "integration_explanation": trace.integration_explanation,
        "historical_influence_applied": True,
        "adaptation_applied": True,
        "execution_authorized": False,
        "review_required": False,
    }

    values[field_name] = 1

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        IntelligenceTrace(**values)


def test_trace_is_frozen() -> None:
    result = make_trace()

    with pytest.raises(FrozenInstanceError):
        result.review_required = True


def test_trace_uses_slots() -> None:
    result = make_trace()

    assert not hasattr(result, "__dict__")


def test_equal_inputs_produce_equal_trace() -> None:
    original = make_trace()

    second = IntelligenceTrace(
        context_id=original.context_id,
        correlation_id=original.correlation_id,
        action=original.action,
        decision_explanation=original.decision_explanation,
        adaptation_explanation=original.adaptation_explanation,
        integration_explanation=original.integration_explanation,
        historical_influence_applied=(original.historical_influence_applied),
        adaptation_applied=original.adaptation_applied,
        execution_authorized=original.execution_authorized,
        review_required=original.review_required,
    )

    assert original == second


def test_trace_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntelligenceTrace.__dataclass_fields__))


def test_trace_contains_no_observability_scoring() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "success_probability",
        "risk_probability",
    }

    assert not (forbidden & set(IntelligenceTrace.__dataclass_fields__))


def test_trace_contains_no_execution_methods() -> None:
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

    public_names = {name for name in dir(IntelligenceTrace) if not name.startswith("_")}

    assert not (forbidden & public_names)
