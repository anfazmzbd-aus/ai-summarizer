"""Tests for V10 M8 intelligence observability summary contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDisposition,
    ExecutionIntegrationMode,
    IntelligenceObservabilityStatus,
    IntelligenceObservabilitySummary,
    OrchestrationDisposition,
    TaskAction,
)


def make_summary(
    *,
    status: IntelligenceObservabilityStatus = (
        IntelligenceObservabilityStatus.ADVISORY
    ),
    adaptation_disposition: AdaptationDisposition = (AdaptationDisposition.ADVISORY),
    orchestration_disposition: OrchestrationDisposition = (
        OrchestrationDisposition.ADVISORY_CONTEXT
    ),
    integration_mode: ExecutionIntegrationMode = (ExecutionIntegrationMode.ADVISORY),
    historical_influence_applied: bool = True,
    adaptation_applied: bool = True,
    execution_authorized: bool = False,
    review_required: bool = False,
    reason_count: int = 3,
) -> IntelligenceObservabilitySummary:
    return IntelligenceObservabilitySummary(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        status=status,
        adaptation_disposition=adaptation_disposition,
        orchestration_disposition=orchestration_disposition,
        integration_mode=integration_mode,
        historical_influence_applied=(historical_influence_applied),
        adaptation_applied=adaptation_applied,
        execution_authorized=execution_authorized,
        review_required=review_required,
        reason_count=reason_count,
    )


def test_status_values_are_stable() -> None:
    assert IntelligenceObservabilityStatus.NORMAL.value == "normal"
    assert IntelligenceObservabilityStatus.ADVISORY.value == "advisory"
    assert IntelligenceObservabilityStatus.CONSTRAINED.value == "constrained"
    assert IntelligenceObservabilityStatus.REVIEW_REQUIRED.value == "review_required"


def test_create_returns_observability_summary() -> None:
    result = make_summary()

    assert isinstance(
        result,
        IntelligenceObservabilitySummary,
    )


def test_context_id_is_preserved() -> None:
    context_id = uuid4()

    result = IntelligenceObservabilitySummary(
        context_id=context_id,
        correlation_id=uuid4(),
        action=TaskAction.SUMMARIZE,
        status=IntelligenceObservabilityStatus.NORMAL,
        adaptation_disposition=AdaptationDisposition.PRESERVE,
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        integration_mode=ExecutionIntegrationMode.PRESERVE,
        historical_influence_applied=False,
        adaptation_applied=False,
        execution_authorized=False,
        review_required=False,
        reason_count=0,
    )

    assert result.context_id == context_id


def test_correlation_id_is_preserved() -> None:
    correlation_id = uuid4()

    result = IntelligenceObservabilitySummary(
        context_id=uuid4(),
        correlation_id=correlation_id,
        action=TaskAction.SUMMARIZE,
        status=IntelligenceObservabilityStatus.NORMAL,
        adaptation_disposition=AdaptationDisposition.PRESERVE,
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        integration_mode=ExecutionIntegrationMode.PRESERVE,
        historical_influence_applied=False,
        adaptation_applied=False,
        execution_authorized=False,
        review_required=False,
        reason_count=0,
    )

    assert result.correlation_id == correlation_id


def test_action_is_preserved() -> None:
    result = IntelligenceObservabilitySummary(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=TaskAction.VERIFY,
        status=IntelligenceObservabilityStatus.NORMAL,
        adaptation_disposition=AdaptationDisposition.PRESERVE,
        orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
        integration_mode=ExecutionIntegrationMode.PRESERVE,
        historical_influence_applied=False,
        adaptation_applied=False,
        execution_authorized=False,
        review_required=False,
        reason_count=0,
    )

    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "status",
    list(IntelligenceObservabilityStatus),
)
def test_all_statuses_are_representable(
    status: IntelligenceObservabilityStatus,
) -> None:
    result = make_summary(
        status=status,
    )

    assert result.status is status


@pytest.mark.parametrize(
    "adaptation_disposition",
    list(AdaptationDisposition),
)
def test_all_adaptation_dispositions_are_representable(
    adaptation_disposition: AdaptationDisposition,
) -> None:
    result = make_summary(
        adaptation_disposition=adaptation_disposition,
    )

    assert result.adaptation_disposition is adaptation_disposition


@pytest.mark.parametrize(
    "orchestration_disposition",
    list(OrchestrationDisposition),
)
def test_all_orchestration_dispositions_are_representable(
    orchestration_disposition: OrchestrationDisposition,
) -> None:
    result = make_summary(
        orchestration_disposition=orchestration_disposition,
    )

    assert result.orchestration_disposition is orchestration_disposition


@pytest.mark.parametrize(
    "integration_mode",
    list(ExecutionIntegrationMode),
)
def test_all_integration_modes_are_representable(
    integration_mode: ExecutionIntegrationMode,
) -> None:
    result = make_summary(
        integration_mode=integration_mode,
    )

    assert result.integration_mode is integration_mode


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
    result = make_summary()

    assert isinstance(
        getattr(result, field_name),
        bool,
    )


def test_reason_count_is_preserved() -> None:
    result = make_summary(
        reason_count=9,
    )

    assert result.reason_count == 9


def test_zero_reason_count_is_allowed() -> None:
    result = make_summary(
        reason_count=0,
    )

    assert result.reason_count == 0


def test_context_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        IntelligenceObservabilitySummary(
            context_id="invalid",
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            status=IntelligenceObservabilityStatus.NORMAL,
            adaptation_disposition=(AdaptationDisposition.PRESERVE),
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            integration_mode=(ExecutionIntegrationMode.PRESERVE),
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
        )


def test_correlation_id_must_be_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        IntelligenceObservabilitySummary(
            context_id=uuid4(),
            correlation_id="invalid",
            action=TaskAction.SUMMARIZE,
            status=IntelligenceObservabilityStatus.NORMAL,
            adaptation_disposition=(AdaptationDisposition.PRESERVE),
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            integration_mode=(ExecutionIntegrationMode.PRESERVE),
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
        )


def test_action_must_be_task_action() -> None:
    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        IntelligenceObservabilitySummary(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action="summarize",
            status=IntelligenceObservabilityStatus.NORMAL,
            adaptation_disposition=(AdaptationDisposition.PRESERVE),
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            integration_mode=(ExecutionIntegrationMode.PRESERVE),
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
        )


def test_status_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("status must be an " "IntelligenceObservabilityStatus"),
    ):
        IntelligenceObservabilitySummary(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            status="normal",
            adaptation_disposition=(AdaptationDisposition.PRESERVE),
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            integration_mode=(ExecutionIntegrationMode.PRESERVE),
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
        )


def test_adaptation_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("adaptation_disposition must be an " "AdaptationDisposition"),
    ):
        IntelligenceObservabilitySummary(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            status=IntelligenceObservabilityStatus.NORMAL,
            adaptation_disposition="preserve",
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            integration_mode=(ExecutionIntegrationMode.PRESERVE),
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
        )


def test_orchestration_disposition_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("orchestration_disposition must be an " "OrchestrationDisposition"),
    ):
        IntelligenceObservabilitySummary(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            status=IntelligenceObservabilityStatus.NORMAL,
            adaptation_disposition=(AdaptationDisposition.PRESERVE),
            orchestration_disposition="no_change",
            integration_mode=(ExecutionIntegrationMode.PRESERVE),
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
        )


def test_integration_mode_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match=("integration_mode must be an " "ExecutionIntegrationMode"),
    ):
        IntelligenceObservabilitySummary(
            context_id=uuid4(),
            correlation_id=uuid4(),
            action=TaskAction.SUMMARIZE,
            status=IntelligenceObservabilityStatus.NORMAL,
            adaptation_disposition=(AdaptationDisposition.PRESERVE),
            orchestration_disposition=(OrchestrationDisposition.NO_CHANGE),
            integration_mode="preserve",
            historical_influence_applied=False,
            adaptation_applied=False,
            execution_authorized=False,
            review_required=False,
            reason_count=0,
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
    values = {
        "context_id": uuid4(),
        "correlation_id": uuid4(),
        "action": TaskAction.SUMMARIZE,
        "status": IntelligenceObservabilityStatus.NORMAL,
        "adaptation_disposition": (AdaptationDisposition.PRESERVE),
        "orchestration_disposition": (OrchestrationDisposition.NO_CHANGE),
        "integration_mode": (ExecutionIntegrationMode.PRESERVE),
        "historical_influence_applied": False,
        "adaptation_applied": False,
        "execution_authorized": False,
        "review_required": False,
        "reason_count": 0,
    }

    values[field_name] = 1

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        IntelligenceObservabilitySummary(**values)


def test_reason_count_must_be_integer() -> None:
    with pytest.raises(
        TypeError,
        match="reason_count must be an integer",
    ):
        make_summary(
            reason_count=1.5,
        )


def test_reason_count_rejects_boolean() -> None:
    with pytest.raises(
        TypeError,
        match="reason_count must be an integer",
    ):
        make_summary(
            reason_count=True,
        )


def test_reason_count_must_be_non_negative() -> None:
    with pytest.raises(
        ValueError,
        match=("reason_count must be greater than or equal to 0"),
    ):
        make_summary(
            reason_count=-1,
        )


def test_summary_is_frozen() -> None:
    result = make_summary()

    with pytest.raises(FrozenInstanceError):
        result.status = IntelligenceObservabilityStatus.NORMAL


def test_summary_uses_slots() -> None:
    result = make_summary()

    assert not hasattr(result, "__dict__")


def test_equal_inputs_produce_equal_summary() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    values = {
        "context_id": context_id,
        "correlation_id": correlation_id,
        "action": TaskAction.SUMMARIZE,
        "status": IntelligenceObservabilityStatus.ADVISORY,
        "adaptation_disposition": (AdaptationDisposition.ADVISORY),
        "orchestration_disposition": (OrchestrationDisposition.ADVISORY_CONTEXT),
        "integration_mode": (ExecutionIntegrationMode.ADVISORY),
        "historical_influence_applied": True,
        "adaptation_applied": True,
        "execution_authorized": False,
        "review_required": False,
        "reason_count": 3,
    }

    first = IntelligenceObservabilitySummary(**values)
    second = IntelligenceObservabilitySummary(**values)

    assert first == second


def test_summary_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntelligenceObservabilitySummary.__dataclass_fields__))


def test_summary_contains_no_advanced_analytics() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "success_probability",
        "risk_probability",
        "prediction",
    }

    assert not (forbidden & set(IntelligenceObservabilitySummary.__dataclass_fields__))


def test_summary_contains_no_execution_methods() -> None:
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
        name
        for name in dir(IntelligenceObservabilitySummary)
        if not name.startswith("_")
    }

    assert not (forbidden & public_names)
