"""Tests for V10 M9 failure semantics and boundary stress."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDisposition,
    BoundaryStressCase,
    BoundaryStressCategory,
    BoundaryStressEvaluator,
    DirectiveValidationStatus,
    ExecutionIntegrationDirective,
    ExecutionIntegrationMode,
    IntelligenceObservabilityIntegrationBoundary,
    IntelligenceObservabilitySnapshot,
    IntelligenceOrchestrationHandoff,
    OrchestrationDirective,
    OrchestrationDirectiveGuard,
    OrchestrationDisposition,
    TaskAction,
)
from app.tests.intelligence.test_observability_integration import (
    make_chain,
)


def make_case(
    *,
    case_id: str = "STRESS-001",
    category: BoundaryStressCategory = (BoundaryStressCategory.PROVENANCE),
    description: str = "test boundary stress",
) -> BoundaryStressCase:
    return BoundaryStressCase(
        case_id=case_id,
        category=category,
        description=description,
    )


def test_category_values_are_stable() -> None:
    assert BoundaryStressCategory.PROVENANCE.value == "provenance"
    assert BoundaryStressCategory.AUTHORITY.value == "authority"
    assert BoundaryStressCategory.STATE_CONSISTENCY.value == "state_consistency"
    assert BoundaryStressCategory.HANDOFF.value == "handoff"
    assert BoundaryStressCategory.OBSERVABILITY.value == "observability"
    assert BoundaryStressCategory.TYPE_SAFETY.value == "type_safety"


def test_case_requires_non_empty_id() -> None:
    with pytest.raises(
        ValueError,
        match="case_id must not be empty",
    ):
        BoundaryStressCase(
            case_id="",
            category=BoundaryStressCategory.PROVENANCE,
            description="test",
        )


def test_case_requires_valid_category() -> None:
    with pytest.raises(
        TypeError,
        match=("category must be a BoundaryStressCategory"),
    ):
        BoundaryStressCase(
            case_id="STRESS-001",
            category="provenance",
            description="test",
        )


def test_evaluator_passes_when_expected_exception_occurs() -> None:
    result = BoundaryStressEvaluator().evaluate(
        make_case(),
        lambda: (_ for _ in ()).throw(ValueError("expected rejection")),
        ValueError,
    )

    assert result.passed is True
    assert result.exception_type == "ValueError"


def test_evaluator_fails_when_no_exception_occurs() -> None:
    result = BoundaryStressEvaluator().evaluate(
        make_case(),
        lambda: object(),
        ValueError,
    )

    assert result.passed is False
    assert result.exception_type is None


def test_evaluator_fails_on_unexpected_exception() -> None:
    result = BoundaryStressEvaluator().evaluate(
        make_case(),
        lambda: (_ for _ in ()).throw(TypeError("wrong failure")),
        ValueError,
    )

    assert result.passed is False
    assert result.exception_type == "TypeError"


def test_no_change_execution_escalation_is_rejected() -> None:
    directive = OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=(AdaptationDisposition.PRESERVE),
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        execution_change_allowed=True,
        review_required=False,
        reasons=("invalid escalation",),
    )

    result = BoundaryStressEvaluator().evaluate(
        BoundaryStressCase(
            case_id="STRESS-AUTH-001",
            category=BoundaryStressCategory.AUTHORITY,
            description=("NO_CHANGE cannot authorize execution change"),
        ),
        lambda: OrchestrationDirectiveGuard().validate(directive),
        RuntimeError,
    )

    # Guard rejects by returning REJECTED rather than raising.
    # Therefore test the fail-closed state directly instead.
    guarded = OrchestrationDirectiveGuard().validate(directive)

    assert guarded.status is DirectiveValidationStatus.REJECTED
    assert guarded.execution_authorized is False
    assert result.passed is False


def test_advisory_execution_escalation_is_rejected() -> None:
    directive = OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=(AdaptationDisposition.ADVISORY),
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        execution_change_allowed=True,
        review_required=False,
        reasons=("invalid escalation",),
    )

    guarded = OrchestrationDirectiveGuard().validate(directive)

    assert guarded.status is DirectiveValidationStatus.REJECTED
    assert guarded.execution_authorized is False


def test_review_execution_escalation_is_rejected() -> None:
    directive = OrchestrationDirective.create(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        adaptation_disposition=(AdaptationDisposition.REVIEW),
        orchestration_disposition=(OrchestrationDisposition.REVIEW_REQUIRED),
        execution_change_allowed=True,
        review_required=True,
        reasons=("invalid escalation",),
    )

    guarded = OrchestrationDirectiveGuard().validate(directive)

    assert guarded.status is DirectiveValidationStatus.REJECTED
    assert guarded.execution_authorized is False


def test_rejected_validation_cannot_cross_handoff() -> None:
    from app.tests.intelligence.test_intelligence_orchestration_handoff import (
        make_chain,
    )

    outcome, directive, _ = make_chain()

    invalid_directive = OrchestrationDirective.create(
        context_id=directive.context_id,
        correlation_id=directive.correlation_id,
        action=directive.action,
        adaptation_disposition=(directive.adaptation_disposition),
        orchestration_disposition=(OrchestrationDisposition.ADVISORY_CONTEXT),
        execution_change_allowed=True,
        review_required=False,
        reasons=("invalid escalation",),
    )

    validation = OrchestrationDirectiveGuard().validate(invalid_directive)

    assert validation.status is DirectiveValidationStatus.REJECTED

    with pytest.raises(
        ValueError,
        match=("handoff requires a valid directive validation"),
    ):
        IntelligenceOrchestrationHandoff(
            context_id=outcome.context_id,
            correlation_id=outcome.correlation_id,
            action=outcome.action,
            adaptive_outcome=outcome,
            directive=invalid_directive,
            validation=validation,
            orchestration_disposition=(invalid_directive.orchestration_disposition),
            execution_authorized=False,
            review_required=False,
        )


def test_preserve_integration_cannot_authorize_execution() -> None:
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


def test_advisory_integration_cannot_authorize_execution() -> None:
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


def test_review_integration_cannot_authorize_execution() -> None:
    with pytest.raises(
        ValueError,
        match=("REVIEW mode cannot authorize execution changes"),
    ):
        ExecutionIntegrationDirective(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            mode=ExecutionIntegrationMode.REVIEW,
            preserve_existing_behavior=True,
            execution_change_authorized=True,
            bounded_constraint_required=False,
            review_required=True,
            reasons=(),
        )


def test_constrained_mode_requires_authority() -> None:
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


def test_constrained_mode_requires_constraint_flag() -> None:
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


def test_observability_snapshot_rejects_context_corruption() -> None:
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


def test_observability_snapshot_rejects_authority_corruption() -> None:
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


def test_observability_snapshot_rejects_review_corruption() -> None:
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


def test_observability_integration_rejects_invalid_summary() -> None:
    trace, _, event = make_chain()

    with pytest.raises(
        TypeError,
        match=("summary must be an " "IntelligenceObservabilitySummary"),
    ):
        IntelligenceObservabilityIntegrationBoundary().compose(
            trace,
            "invalid",
            event,
        )


def test_stress_evaluator_evaluate_all() -> None:
    evaluator = BoundaryStressEvaluator()

    cases = (
        (
            make_case(
                case_id="STRESS-TYPE-001",
                category=(BoundaryStressCategory.TYPE_SAFETY),
                description="reject invalid value",
            ),
            lambda: (_ for _ in ()).throw(TypeError("invalid")),
            TypeError,
        ),
        (
            make_case(
                case_id="STRESS-PROV-001",
                category=(BoundaryStressCategory.PROVENANCE),
                description="reject provenance mismatch",
            ),
            lambda: (_ for _ in ()).throw(ValueError("mismatch")),
            ValueError,
        ),
    )

    results = evaluator.evaluate_all(cases)

    assert len(results) == 2
    assert all(result.passed for result in results)


def test_stress_evaluator_requires_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="cases must be a tuple",
    ):
        BoundaryStressEvaluator().evaluate_all([])


def test_stress_result_contains_no_runtime_configuration() -> None:
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
        "streaming",
    }

    assert not (
        forbidden
        & set(
            __import__(
                "app.intelligence",
                fromlist=["BoundaryStressResult"],
            ).BoundaryStressResult.__dataclass_fields__
        )
    )


def test_stress_evaluator_has_no_runtime_interface() -> None:
    forbidden = {
        "execute",
        "run",
        "retry",
        "replan",
        "adapt",
        "apply_runtime",
        "select_strategy",
        "switch_provider",
        "modify_runtime",
    }

    public_names = {
        name for name in dir(BoundaryStressEvaluator) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_stress_evaluator_public_interface_is_bounded() -> None:
    public_names = {
        name for name in dir(BoundaryStressEvaluator) if not name.startswith("_")
    }

    assert public_names == {
        "evaluate",
        "evaluate_all",
    }
