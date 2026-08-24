"""Tests for V10 M7 existing execution integration adapter."""

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
    ExecutionIntegrationDirective,
    ExecutionIntegrationMode,
    ExistingExecutionIntegrationAdapter,
    ExperienceInformedDecisionBoundary,
    IntelligenceOrchestrationHandoffBoundary,
    OrchestrationDirectiveGuard,
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


def make_handoff(
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

    return IntelligenceOrchestrationHandoffBoundary().compose(
        outcome,
        directive,
        validation,
    )


def test_mode_values_are_stable() -> None:
    assert ExecutionIntegrationMode.PRESERVE.value == "preserve"
    assert ExecutionIntegrationMode.ADVISORY.value == "advisory"
    assert ExecutionIntegrationMode.CONSTRAINED.value == "constrained"
    assert ExecutionIntegrationMode.REVIEW.value == "review"


def test_adapter_returns_execution_integration_directive() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(make_handoff())

    assert isinstance(
        result,
        ExecutionIntegrationDirective,
    )


@pytest.mark.parametrize(
    "disposition,expected_mode",
    [
        (
            DecisionSupportDisposition.PRESERVE,
            ExecutionIntegrationMode.PRESERVE,
        ),
        (
            DecisionSupportDisposition.ADVISORY,
            ExecutionIntegrationMode.ADVISORY,
        ),
        (
            DecisionSupportDisposition.CAUTION,
            ExecutionIntegrationMode.CONSTRAINED,
        ),
        (
            DecisionSupportDisposition.REVIEW,
            ExecutionIntegrationMode.REVIEW,
        ),
    ],
)
def test_complete_integration_mapping(
    disposition: DecisionSupportDisposition,
    expected_mode: ExecutionIntegrationMode,
) -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=disposition,
        )
    )

    assert result.mode is expected_mode


def test_preserve_mode_keeps_existing_behavior() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert result.preserve_existing_behavior is True
    assert result.execution_change_authorized is False
    assert result.bounded_constraint_required is False
    assert result.review_required is False


def test_advisory_mode_keeps_existing_behavior() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.ADVISORY,
        )
    )

    assert result.preserve_existing_behavior is True
    assert result.execution_change_authorized is False
    assert result.bounded_constraint_required is False
    assert result.review_required is False


def test_constrained_mode_requires_bounded_constraint() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.CAUTION,
        )
    )

    assert result.preserve_existing_behavior is True
    assert result.execution_change_authorized is True
    assert result.bounded_constraint_required is True
    assert result.review_required is False


def test_review_mode_requires_review_only() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.REVIEW,
        )
    )

    assert result.preserve_existing_behavior is True
    assert result.execution_change_authorized is False
    assert result.bounded_constraint_required is False
    assert result.review_required is True


def test_adapter_preserves_context_id() -> None:
    handoff = make_handoff()

    result = ExistingExecutionIntegrationAdapter().adapt(handoff)

    assert result.context_id == handoff.context_id


def test_adapter_preserves_correlation_id() -> None:
    handoff = make_handoff()

    result = ExistingExecutionIntegrationAdapter().adapt(handoff)

    assert result.correlation_id == handoff.correlation_id


def test_adapter_preserves_action() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            action=TaskAction.VERIFY,
        )
    )

    assert result.action is TaskAction.VERIFY


def test_adapter_preserves_validation_reasons() -> None:
    handoff = make_handoff()

    result = ExistingExecutionIntegrationAdapter().adapt(handoff)

    upstream = handoff.validation.reasons

    assert result.reasons[: len(upstream)] == upstream


def test_preserve_reason_is_added() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.PRESERVE,
        )
    )

    assert any(
        "existing execution behavior remains unchanged" in reason
        for reason in result.reasons
    )


def test_advisory_reason_is_added() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.ADVISORY,
        )
    )

    assert any(
        "advisory intelligence context is preserved" in reason
        for reason in result.reasons
    )


def test_constraint_reason_is_added() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.CAUTION,
        )
    )

    assert any(
        "approved bounded constraints are required" in reason
        for reason in result.reasons
    )


def test_review_reason_is_added() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(
        make_handoff(
            disposition=DecisionSupportDisposition.REVIEW,
        )
    )

    assert any("review-oriented handling" in reason for reason in result.reasons)


def test_adapter_rejects_invalid_handoff() -> None:
    with pytest.raises(
        TypeError,
        match=("handoff must be an " "IntelligenceOrchestrationHandoff"),
    ):
        ExistingExecutionIntegrationAdapter().adapt("invalid")


def test_directive_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        ExecutionIntegrationDirective(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.PRESERVE,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_directive_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.PRESERVE,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_directive_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            mode=ExecutionIntegrationMode.PRESERVE,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_directive_mode_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("mode must be an ExecutionIntegrationMode"),
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode="preserve",
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "preserve_existing_behavior",
        "execution_change_authorized",
        "bounded_constraint_required",
        "review_required",
    ],
)
def test_boolean_fields_require_bool(
    field_name: str,
) -> None:
    values = {
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "action": TaskAction.SUMMARIZE,
        "mode": ExecutionIntegrationMode.PRESERVE,
        "preserve_existing_behavior": True,
        "execution_change_authorized": False,
        "bounded_constraint_required": False,
        "review_required": False,
        "reasons": (),
    }

    values[field_name] = 1

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        ExecutionIntegrationDirective(**values)


def test_preserve_mode_rejects_execution_change() -> None:
    with pytest.raises(
        ValueError,
        match=("PRESERVE mode cannot authorize execution changes"),
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.PRESERVE,
            preserve_existing_behavior=True,
            execution_change_authorized=True,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_advisory_mode_rejects_execution_change() -> None:
    with pytest.raises(
        ValueError,
        match=("ADVISORY mode cannot authorize execution changes"),
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.ADVISORY,
            preserve_existing_behavior=True,
            execution_change_authorized=True,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_constrained_mode_requires_execution_authority() -> None:
    with pytest.raises(
        ValueError,
        match=("CONSTRAINED mode requires execution change authority"),
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.CONSTRAINED,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=True,
            review_required=False,
            reasons=(),
        )


def test_constrained_mode_requires_constraint() -> None:
    with pytest.raises(
        ValueError,
        match=("CONSTRAINED mode requires bounded constraints"),
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.CONSTRAINED,
            preserve_existing_behavior=True,
            execution_change_authorized=True,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_review_mode_requires_review() -> None:
    with pytest.raises(
        ValueError,
        match="REVIEW mode requires review",
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.REVIEW,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(),
        )


def test_reasons_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must be a tuple",
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.PRESERVE,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=["reason"],
        )


def test_reasons_must_contain_strings() -> None:
    with pytest.raises(
        TypeError,
        match="reasons must contain strings",
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.PRESERVE,
            preserve_existing_behavior=True,
            execution_change_authorized=False,
            bounded_constraint_required=False,
            review_required=False,
            reasons=(123,),
        )


def test_directive_is_frozen() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(make_handoff())

    with pytest.raises(FrozenInstanceError):
        result.review_required = True


def test_directive_uses_slots() -> None:
    result = ExistingExecutionIntegrationAdapter().adapt(make_handoff())

    assert not hasattr(result, "__dict__")


def test_adapter_is_deterministic() -> None:
    handoff = make_handoff(
        disposition=DecisionSupportDisposition.CAUTION,
    )

    adapter = ExistingExecutionIntegrationAdapter()

    first = adapter.adapt(handoff)
    second = adapter.adapt(handoff)

    assert first == second


def test_adapter_does_not_modify_handoff() -> None:
    handoff = make_handoff()

    before = handoff

    ExistingExecutionIntegrationAdapter().adapt(handoff)

    assert handoff == before


def test_directive_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(ExecutionIntegrationDirective.__dataclass_fields__))


def test_adapter_has_no_runtime_interface() -> None:
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
        name
        for name in dir(ExistingExecutionIntegrationAdapter)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_adapter_exposes_only_adapt() -> None:
    public_names = {
        name
        for name in dir(ExistingExecutionIntegrationAdapter)
        if not name.startswith("_")
    }

    assert public_names == {"adapt"}
