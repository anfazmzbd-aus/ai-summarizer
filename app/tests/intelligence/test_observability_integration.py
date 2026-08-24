"""Tests for V10 M8 explainability integration and safety."""

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
    IntelligenceObservabilityEvaluator,
    IntelligenceObservabilityIntegrationBoundary,
    IntelligenceObservabilitySnapshot,
    IntelligenceObservabilityStatus,
    IntelligenceTraceBuilder,
    ObservabilityEventBuilder,
    OrchestrationDisposition,
    TaskAction,
)


def make_chain(
    *,
    mode: ExecutionIntegrationMode = (ExecutionIntegrationMode.ADVISORY),
):
    context_id = uuid4()
    correlation_id = uuid4()
    action = TaskAction.SUMMARIZE

    mode_map = {
        ExecutionIntegrationMode.PRESERVE: (
            AdaptationDisposition.PRESERVE,
            DecisionSupportDisposition.PRESERVE,
            AdaptationEligibilityStatus.INELIGIBLE,
            OrchestrationDisposition.NO_CHANGE,
            False,
            False,
            False,
            False,
        ),
        ExecutionIntegrationMode.ADVISORY: (
            AdaptationDisposition.ADVISORY,
            DecisionSupportDisposition.ADVISORY,
            AdaptationEligibilityStatus.ELIGIBLE,
            OrchestrationDisposition.ADVISORY_CONTEXT,
            True,
            True,
            False,
            False,
        ),
        ExecutionIntegrationMode.CONSTRAINED: (
            AdaptationDisposition.CONSTRAIN,
            DecisionSupportDisposition.CAUTION,
            AdaptationEligibilityStatus.ELIGIBLE,
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            True,
            True,
            True,
            False,
        ),
        ExecutionIntegrationMode.REVIEW: (
            AdaptationDisposition.REVIEW,
            DecisionSupportDisposition.REVIEW,
            AdaptationEligibilityStatus.REVIEW_ONLY,
            OrchestrationDisposition.REVIEW_REQUIRED,
            True,
            True,
            False,
            True,
        ),
    }

    (
        adaptation_disposition,
        policy_disposition,
        eligibility_status,
        orchestration_disposition,
        influence,
        adaptation_applied,
        execution_authorized,
        review_required,
    ) = mode_map[mode]

    decision = DecisionExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        sample_count=3,
        effective_count=3,
        degraded_count=0,
        ineffective_count=0,
        unknown_count=0,
        evidence_strength=EvidenceStrength.ESTABLISHED,
        evidence_status=(
            EvidenceAssessmentStatus.SUPPORTIVE
            if influence
            else EvidenceAssessmentStatus.MIXED
        ),
        support_status=(
            DecisionSupportStatus.SUPPORTED
            if influence
            else DecisionSupportStatus.NEUTRAL
        ),
        disposition=policy_disposition,
        historical_influence_applied=influence,
        evidence_reasons=("evidence",),
        support_reasons=("support",),
        policy_reasons=("policy",),
        decision_reasons=("decision",),
    )

    adaptation = AdaptationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        policy_disposition=policy_disposition,
        eligibility_status=eligibility_status,
        adaptation_disposition=adaptation_disposition,
        historical_influence_applied=influence,
        adaptation_applied=adaptation_applied,
        informed_decision_reasons=("decision",),
        eligibility_reasons=("eligibility",),
        adaptation_reasons=("adaptation",),
    )

    integration = IntegrationExplanation(
        context_id=context_id,
        correlation_id=correlation_id,
        action=action,
        adaptation_disposition=adaptation_disposition,
        orchestration_disposition=orchestration_disposition,
        validation_status=DirectiveValidationStatus.VALID,
        integration_mode=mode,
        execution_authorized=execution_authorized,
        bounded_constraint_required=(mode is ExecutionIntegrationMode.CONSTRAINED),
        review_required=review_required,
        orchestration_reasons=("orchestration",),
        validation_reasons=("validation",),
        integration_reasons=("integration",),
    )

    trace = IntelligenceTraceBuilder().build(
        decision,
        adaptation,
        integration,
    )

    summary = IntelligenceObservabilityEvaluator().evaluate(trace)

    event = ObservabilityEventBuilder().build(summary)

    return trace, summary, event


def make_snapshot(
    *,
    mode: ExecutionIntegrationMode = (ExecutionIntegrationMode.ADVISORY),
) -> IntelligenceObservabilitySnapshot:
    trace, summary, event = make_chain(
        mode=mode,
    )

    return IntelligenceObservabilityIntegrationBoundary().compose(
        trace,
        summary,
        event,
    )


def test_boundary_returns_snapshot() -> None:
    result = make_snapshot()

    assert isinstance(
        result,
        IntelligenceObservabilitySnapshot,
    )


def test_chain_objects_are_preserved() -> None:
    trace, summary, event = make_chain()

    result = IntelligenceObservabilityIntegrationBoundary().compose(
        trace,
        summary,
        event,
    )

    assert result.trace is trace
    assert result.summary is summary
    assert result.event is event


def test_provenance_is_preserved() -> None:
    result = make_snapshot()

    assert result.context_id == result.trace.context_id
    assert result.correlation_id == result.trace.correlation_id
    assert result.action is result.trace.action


@pytest.mark.parametrize(
    "mode,expected_status," "expected_execution,expected_review",
    [
        (
            ExecutionIntegrationMode.PRESERVE,
            IntelligenceObservabilityStatus.NORMAL,
            False,
            False,
        ),
        (
            ExecutionIntegrationMode.ADVISORY,
            IntelligenceObservabilityStatus.ADVISORY,
            False,
            False,
        ),
        (
            ExecutionIntegrationMode.CONSTRAINED,
            IntelligenceObservabilityStatus.CONSTRAINED,
            True,
            False,
        ),
        (
            ExecutionIntegrationMode.REVIEW,
            IntelligenceObservabilityStatus.REVIEW_REQUIRED,
            False,
            True,
        ),
    ],
)
def test_complete_observability_snapshot_matrix(
    mode: ExecutionIntegrationMode,
    expected_status: IntelligenceObservabilityStatus,
    expected_execution: bool,
    expected_review: bool,
) -> None:
    result = make_snapshot(
        mode=mode,
    )

    assert result.status is expected_status
    assert result.execution_authorized is expected_execution
    assert result.review_required is expected_review


def test_reason_count_is_preserved() -> None:
    result = make_snapshot()

    assert result.reason_count == result.summary.reason_count
    assert result.reason_count == result.event.reason_count


def test_diagnostic_code_is_preserved() -> None:
    result = make_snapshot()

    assert result.diagnostic_code == result.event.diagnostic_code


def test_invalid_trace_is_rejected() -> None:
    _, summary, event = make_chain()

    with pytest.raises(
        TypeError,
        match="trace must be an IntelligenceTrace",
    ):
        (
            IntelligenceObservabilityIntegrationBoundary().compose(
                "invalid",
                summary,
                event,
            )
        )


def test_invalid_summary_is_rejected() -> None:
    trace, _, event = make_chain()

    with pytest.raises(
        TypeError,
        match=("summary must be an " "IntelligenceObservabilitySummary"),
    ):
        (
            IntelligenceObservabilityIntegrationBoundary().compose(
                trace,
                "invalid",
                event,
            )
        )


def test_invalid_event_is_rejected() -> None:
    trace, summary, _ = make_chain()

    with pytest.raises(
        TypeError,
        match=("event must be an " "IntelligenceObservabilityEvent"),
    ):
        (
            IntelligenceObservabilityIntegrationBoundary().compose(
                trace,
                summary,
                "invalid",
            )
        )


def test_snapshot_context_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    with pytest.raises(
        ValueError,
        match="context_id must match trace",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=uuid4(),
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=summary.reason_count,
            diagnostic_code=event.diagnostic_code,
        )


def test_snapshot_correlation_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    with pytest.raises(
        ValueError,
        match="correlation_id must match trace",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=uuid4(),
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=summary.reason_count,
            diagnostic_code=event.diagnostic_code,
        )


def test_summary_status_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    wrong_status = (
        IntelligenceObservabilityStatus.NORMAL
        if summary.status is not IntelligenceObservabilityStatus.NORMAL
        else IntelligenceObservabilityStatus.ADVISORY
    )

    with pytest.raises(
        ValueError,
        match="status must match summary",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=wrong_status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=summary.reason_count,
            diagnostic_code=event.diagnostic_code,
        )


def test_execution_authority_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    with pytest.raises(
        ValueError,
        match="execution_authorized must match trace",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=(not trace.execution_authorized),
            review_required=trace.review_required,
            reason_count=summary.reason_count,
            diagnostic_code=event.diagnostic_code,
        )


def test_review_requirement_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    with pytest.raises(
        ValueError,
        match="review_required must match trace",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=(not trace.review_required),
            reason_count=summary.reason_count,
            diagnostic_code=event.diagnostic_code,
        )


def test_reason_count_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    with pytest.raises(
        ValueError,
        match="reason_count must match summary",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=summary.reason_count + 1,
            diagnostic_code=event.diagnostic_code,
        )


def test_diagnostic_code_mismatch_is_rejected() -> None:
    trace, summary, event = make_chain()

    with pytest.raises(
        ValueError,
        match="diagnostic_code must match event",
    ):
        IntelligenceObservabilitySnapshot(
            context_id=trace.context_id,
            correlation_id=trace.correlation_id,
            action=trace.action,
            trace=trace,
            summary=summary,
            event=event,
            status=summary.status,
            severity=event.severity,
            historical_influence_applied=(trace.historical_influence_applied),
            adaptation_applied=trace.adaptation_applied,
            execution_authorized=trace.execution_authorized,
            review_required=trace.review_required,
            reason_count=summary.reason_count,
            diagnostic_code="INVALID",
        )


def test_snapshot_is_frozen() -> None:
    result = make_snapshot()

    with pytest.raises(FrozenInstanceError):
        result.review_required = True


def test_snapshot_uses_slots() -> None:
    result = make_snapshot()

    assert not hasattr(result, "__dict__")


def test_boundary_is_deterministic() -> None:
    trace, summary, event = make_chain(
        mode=ExecutionIntegrationMode.CONSTRAINED,
    )

    boundary = IntelligenceObservabilityIntegrationBoundary()

    first = boundary.compose(
        trace,
        summary,
        event,
    )

    second = boundary.compose(
        trace,
        summary,
        event,
    )

    assert first == second


def test_boundary_does_not_modify_inputs() -> None:
    trace, summary, event = make_chain()

    before = trace, summary, event

    (
        IntelligenceObservabilityIntegrationBoundary().compose(
            trace,
            summary,
            event,
        )
    )

    assert before == (
        trace,
        summary,
        event,
    )


def test_snapshot_contains_no_timestamp() -> None:
    assert "timestamp" not in IntelligenceObservabilitySnapshot.__dataclass_fields__


def test_snapshot_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntelligenceObservabilitySnapshot.__dataclass_fields__))


def test_snapshot_contains_no_advanced_analytics() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "success_probability",
        "prediction",
    }

    assert not (forbidden & set(IntelligenceObservabilitySnapshot.__dataclass_fields__))


def test_boundary_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "emit",
        "publish",
        "send",
        "log",
        "retry",
        "replan",
        "adapt",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
    }

    public_names = {
        name
        for name in dir(IntelligenceObservabilityIntegrationBoundary)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_boundary_exposes_only_compose() -> None:
    public_names = {
        name
        for name in dir(IntelligenceObservabilityIntegrationBoundary)
        if not name.startswith("_")
    }

    assert public_names == {"compose"}
