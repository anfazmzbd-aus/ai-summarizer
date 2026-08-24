"""Tests for V10 M8 intelligence observability summary evaluation."""

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
    IntelligenceObservabilityEvaluator,
    IntelligenceObservabilityStatus,
    IntelligenceObservabilitySummary,
    IntelligenceTrace,
    OrchestrationDisposition,
    TaskAction,
)


def make_decision_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
    historical_influence_applied: bool,
) -> DecisionExplanation:
    if historical_influence_applied:
        disposition = DecisionSupportDisposition.ADVISORY
        support_status = DecisionSupportStatus.SUPPORTED
        evidence_status = EvidenceAssessmentStatus.SUPPORTIVE
    else:
        disposition = DecisionSupportDisposition.PRESERVE
        support_status = DecisionSupportStatus.NEUTRAL
        evidence_status = EvidenceAssessmentStatus.MIXED

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
        evidence_status=evidence_status,
        support_status=support_status,
        disposition=disposition,
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
    disposition: AdaptationDisposition,
) -> AdaptationExplanation:
    if disposition is AdaptationDisposition.PRESERVE:
        policy_disposition = DecisionSupportDisposition.PRESERVE
        eligibility_status = AdaptationEligibilityStatus.INELIGIBLE
        influence = False
        applied = False

    elif disposition is AdaptationDisposition.ADVISORY:
        policy_disposition = DecisionSupportDisposition.ADVISORY
        eligibility_status = AdaptationEligibilityStatus.ELIGIBLE
        influence = True
        applied = True

    elif disposition is AdaptationDisposition.CONSTRAIN:
        policy_disposition = DecisionSupportDisposition.CAUTION
        eligibility_status = AdaptationEligibilityStatus.ELIGIBLE
        influence = True
        applied = True

    else:
        policy_disposition = DecisionSupportDisposition.REVIEW
        eligibility_status = AdaptationEligibilityStatus.REVIEW_ONLY
        influence = True
        applied = True

    return AdaptationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        policy_disposition=policy_disposition,
        eligibility_status=eligibility_status,
        adaptation_disposition=disposition,
        historical_influence_applied=influence,
        adaptation_applied=applied,
        informed_decision_reasons=("decision",),
        eligibility_reasons=("eligibility",),
        adaptation_reasons=("adaptation",),
    )


def make_integration_explanation(
    *,
    context_id,
    correlation_id,
    action: TaskAction,
    adaptation_disposition: AdaptationDisposition,
    mode: ExecutionIntegrationMode,
) -> IntegrationExplanation:
    mapping = {
        ExecutionIntegrationMode.PRESERVE: (
            OrchestrationDisposition.NO_CHANGE,
            False,
            False,
            False,
        ),
        ExecutionIntegrationMode.ADVISORY: (
            OrchestrationDisposition.ADVISORY_CONTEXT,
            False,
            False,
            False,
        ),
        ExecutionIntegrationMode.CONSTRAINED: (
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            True,
            True,
            False,
        ),
        ExecutionIntegrationMode.REVIEW: (
            OrchestrationDisposition.REVIEW_REQUIRED,
            False,
            False,
            True,
        ),
    }

    (
        orchestration_disposition,
        execution_authorized,
        bounded_constraint_required,
        review_required,
    ) = mapping[mode]

    return IntegrationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        adaptation_disposition=adaptation_disposition,
        orchestration_disposition=orchestration_disposition,
        validation_status=DirectiveValidationStatus.VALID,
        integration_mode=mode,
        execution_authorized=execution_authorized,
        bounded_constraint_required=(bounded_constraint_required),
        review_required=review_required,
        orchestration_reasons=("orchestration",),
        validation_reasons=("validation",),
        integration_reasons=("integration",),
    )


def make_trace(
    *,
    adaptation_disposition: AdaptationDisposition = (AdaptationDisposition.ADVISORY),
    integration_mode: ExecutionIntegrationMode = (ExecutionIntegrationMode.ADVISORY),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> IntelligenceTrace:
    context_id = uuid4()
    correlation_id = uuid4()

    adaptation = make_adaptation_explanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        disposition=adaptation_disposition,
    )

    decision = make_decision_explanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        historical_influence_applied=(adaptation.historical_influence_applied),
    )

    integration = make_integration_explanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        adaptation_disposition=adaptation_disposition,
        mode=integration_mode,
    )

    return IntelligenceTrace(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        decision_explanation=decision,
        adaptation_explanation=adaptation,
        integration_explanation=integration,
        historical_influence_applied=(adaptation.historical_influence_applied),
        adaptation_applied=adaptation.adaptation_applied,
        execution_authorized=integration.execution_authorized,
        review_required=integration.review_required,
    )


def test_evaluator_returns_observability_summary() -> None:
    result = IntelligenceObservabilityEvaluator().evaluate(make_trace())

    assert isinstance(
        result,
        IntelligenceObservabilitySummary,
    )


@pytest.mark.parametrize(
    "adaptation_disposition,integration_mode,expected_status",
    [
        (
            AdaptationDisposition.PRESERVE,
            ExecutionIntegrationMode.PRESERVE,
            IntelligenceObservabilityStatus.NORMAL,
        ),
        (
            AdaptationDisposition.ADVISORY,
            ExecutionIntegrationMode.ADVISORY,
            IntelligenceObservabilityStatus.ADVISORY,
        ),
        (
            AdaptationDisposition.CONSTRAIN,
            ExecutionIntegrationMode.CONSTRAINED,
            IntelligenceObservabilityStatus.CONSTRAINED,
        ),
        (
            AdaptationDisposition.REVIEW,
            ExecutionIntegrationMode.REVIEW,
            IntelligenceObservabilityStatus.REVIEW_REQUIRED,
        ),
    ],
)
def test_complete_observability_status_mapping(
    adaptation_disposition: AdaptationDisposition,
    integration_mode: ExecutionIntegrationMode,
    expected_status: IntelligenceObservabilityStatus,
) -> None:
    result = IntelligenceObservabilityEvaluator().evaluate(
        make_trace(
            adaptation_disposition=adaptation_disposition,
            integration_mode=integration_mode,
        )
    )

    assert result.status is expected_status


def test_evaluator_preserves_context_id() -> None:
    trace = make_trace()

    result = IntelligenceObservabilityEvaluator().evaluate(trace)

    assert result.context_id == trace.context_id


def test_evaluator_preserves_correlation_id() -> None:
    trace = make_trace()

    result = IntelligenceObservabilityEvaluator().evaluate(trace)

    assert result.correlation_id == trace.correlation_id


def test_evaluator_preserves_action() -> None:
    trace = make_trace(
        action=TaskAction.VERIFY,
    )

    result = IntelligenceObservabilityEvaluator().evaluate(trace)

    assert result.action is TaskAction.VERIFY


def test_adaptation_disposition_is_derived_from_trace() -> None:
    trace = make_trace(
        adaptation_disposition=AdaptationDisposition.CONSTRAIN,
        integration_mode=ExecutionIntegrationMode.CONSTRAINED,
    )

    result = IntelligenceObservabilityEvaluator().evaluate(trace)

    assert result.adaptation_disposition is AdaptationDisposition.CONSTRAIN


def test_orchestration_disposition_is_derived_from_integration() -> None:
    trace = make_trace(
        adaptation_disposition=AdaptationDisposition.REVIEW,
        integration_mode=ExecutionIntegrationMode.REVIEW,
    )

    result = IntelligenceObservabilityEvaluator().evaluate(trace)

    assert result.orchestration_disposition is OrchestrationDisposition.REVIEW_REQUIRED


def test_integration_mode_is_preserved() -> None:
    trace = make_trace(
        adaptation_disposition=AdaptationDisposition.CONSTRAIN,
        integration_mode=ExecutionIntegrationMode.CONSTRAINED,
    )

    result = IntelligenceObservabilityEvaluator().evaluate(trace)

    assert result.integration_mode is ExecutionIntegrationMode.CONSTRAINED


@pytest.mark.parametrize(
    "adaptation_disposition,integration_mode,"
    "expected_influence,expected_adaptation,"
    "expected_execution,expected_review",
    [
        (
            AdaptationDisposition.PRESERVE,
            ExecutionIntegrationMode.PRESERVE,
            False,
            False,
            False,
            False,
        ),
        (
            AdaptationDisposition.ADVISORY,
            ExecutionIntegrationMode.ADVISORY,
            True,
            True,
            False,
            False,
        ),
        (
            AdaptationDisposition.CONSTRAIN,
            ExecutionIntegrationMode.CONSTRAINED,
            True,
            True,
            True,
            False,
        ),
        (
            AdaptationDisposition.REVIEW,
            ExecutionIntegrationMode.REVIEW,
            True,
            True,
            False,
            True,
        ),
    ],
)
def test_lifecycle_state_is_preserved(
    adaptation_disposition: AdaptationDisposition,
    integration_mode: ExecutionIntegrationMode,
    expected_influence: bool,
    expected_adaptation: bool,
    expected_execution: bool,
    expected_review: bool,
) -> None:
    result = IntelligenceObservabilityEvaluator().evaluate(
        make_trace(
            adaptation_disposition=adaptation_disposition,
            integration_mode=integration_mode,
        )
    )

    assert result.historical_influence_applied is expected_influence
    assert result.adaptation_applied is expected_adaptation
    assert result.execution_authorized is expected_execution
    assert result.review_required is expected_review


def test_reason_count_is_derived_from_all_reason_layers() -> None:
    result = IntelligenceObservabilityEvaluator().evaluate(make_trace())

    # Decision: 4
    # Adaptation: 3
    # Integration: 3
    assert result.reason_count == 10


def test_invalid_trace_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="trace must be an IntelligenceTrace",
    ):
        IntelligenceObservabilityEvaluator().evaluate("invalid")


def test_trace_context_mismatch_is_rejected() -> None:
    trace = make_trace()

    invalid = IntelligenceTrace(
        context_id=uuid4(),
        correlation_id=trace.correlation_id,
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=trace.execution_authorized,
        review_required=trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match=("trace context_id must match decision_explanation"),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_trace_correlation_mismatch_is_rejected() -> None:
    trace = make_trace()

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=uuid4(),
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=trace.execution_authorized,
        review_required=trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match=("trace correlation_id must match " "decision_explanation"),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_trace_action_mismatch_is_rejected() -> None:
    trace = make_trace()

    wrong_action = (
        TaskAction.VERIFY
        if trace.action is TaskAction.SUMMARIZE
        else TaskAction.SUMMARIZE
    )

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=wrong_action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=trace.execution_authorized,
        review_required=trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match="trace action must match decision_explanation",
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_trace_historical_influence_mismatch_is_rejected() -> None:
    trace = make_trace()

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(not trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=trace.execution_authorized,
        review_required=trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match=("trace historical influence must match " "adaptation_explanation"),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_trace_adaptation_state_mismatch_is_rejected() -> None:
    trace = make_trace()

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=not trace.adaptation_applied,
        execution_authorized=trace.execution_authorized,
        review_required=trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match=("trace adaptation state must match " "adaptation_explanation"),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_trace_execution_authority_mismatch_is_rejected() -> None:
    trace = make_trace()

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=not trace.execution_authorized,
        review_required=trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match=("trace execution authority must match " "integration_explanation"),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_trace_review_requirement_mismatch_is_rejected() -> None:
    trace = make_trace()

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=trace.integration_explanation,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=trace.execution_authorized,
        review_required=not trace.review_required,
    )

    with pytest.raises(
        ValueError,
        match=("trace review requirement must match " "integration_explanation"),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_adaptation_disposition_mismatch_is_rejected() -> None:
    trace = make_trace(
        adaptation_disposition=AdaptationDisposition.ADVISORY,
        integration_mode=ExecutionIntegrationMode.ADVISORY,
    )

    integration = make_integration_explanation(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=trace.action,
        adaptation_disposition=AdaptationDisposition.CONSTRAIN,
        mode=ExecutionIntegrationMode.ADVISORY,
    )

    invalid = IntelligenceTrace(
        context_id=trace.context_id,
        correlation_id=trace.correlation_id,
        action=trace.action,
        decision_explanation=trace.decision_explanation,
        adaptation_explanation=trace.adaptation_explanation,
        integration_explanation=integration,
        historical_influence_applied=(trace.historical_influence_applied),
        adaptation_applied=trace.adaptation_applied,
        execution_authorized=integration.execution_authorized,
        review_required=integration.review_required,
    )

    with pytest.raises(
        ValueError,
        match=(
            "adaptation disposition must match across "
            "adaptation and integration explanations"
        ),
    ):
        IntelligenceObservabilityEvaluator().evaluate(invalid)


def test_evaluator_is_deterministic() -> None:
    trace = make_trace(
        adaptation_disposition=AdaptationDisposition.CONSTRAIN,
        integration_mode=ExecutionIntegrationMode.CONSTRAINED,
    )

    evaluator = IntelligenceObservabilityEvaluator()

    first = evaluator.evaluate(trace)
    second = evaluator.evaluate(trace)

    assert first == second


def test_evaluator_does_not_modify_trace() -> None:
    trace = make_trace()

    before = trace

    IntelligenceObservabilityEvaluator().evaluate(trace)

    assert trace == before


def test_evaluator_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "retry",
        "replan",
        "adapt",
        "run",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
    }

    public_names = {
        name
        for name in dir(IntelligenceObservabilityEvaluator)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_evaluator_exposes_only_evaluate() -> None:
    public_names = {
        name
        for name in dir(IntelligenceObservabilityEvaluator)
        if not name.startswith("_")
    }

    assert public_names == {"evaluate"}
