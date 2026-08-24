"""Tests for V10 M8 intelligence observability event boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.intelligence import (
    AdaptationDisposition,
    ExecutionIntegrationMode,
    IntelligenceObservabilityEvent,
    IntelligenceObservabilitySeverity,
    IntelligenceObservabilityStatus,
    IntelligenceObservabilitySummary,
    ObservabilityEventBuilder,
    OrchestrationDisposition,
    TaskAction,
)


def make_summary(
    *,
    status: IntelligenceObservabilityStatus = (
        IntelligenceObservabilityStatus.ADVISORY
    ),
    action: TaskAction = TaskAction.SUMMARIZE,
) -> IntelligenceObservabilitySummary:
    mapping = {
        IntelligenceObservabilityStatus.NORMAL: (
            AdaptationDisposition.PRESERVE,
            OrchestrationDisposition.NO_CHANGE,
            ExecutionIntegrationMode.PRESERVE,
            False,
            False,
            False,
            False,
        ),
        IntelligenceObservabilityStatus.ADVISORY: (
            AdaptationDisposition.ADVISORY,
            OrchestrationDisposition.ADVISORY_CONTEXT,
            ExecutionIntegrationMode.ADVISORY,
            True,
            True,
            False,
            False,
        ),
        IntelligenceObservabilityStatus.CONSTRAINED: (
            AdaptationDisposition.CONSTRAIN,
            OrchestrationDisposition.BOUNDED_CONSTRAINT,
            ExecutionIntegrationMode.CONSTRAINED,
            True,
            True,
            True,
            False,
        ),
        IntelligenceObservabilityStatus.REVIEW_REQUIRED: (
            AdaptationDisposition.REVIEW,
            OrchestrationDisposition.REVIEW_REQUIRED,
            ExecutionIntegrationMode.REVIEW,
            True,
            True,
            False,
            True,
        ),
    }

    (
        adaptation_disposition,
        orchestration_disposition,
        integration_mode,
        historical_influence_applied,
        adaptation_applied,
        execution_authorized,
        review_required,
    ) = mapping[status]

    return IntelligenceObservabilitySummary(
        context_id=uuid4(),
        correlation_id=uuid4(),
        action=action,
        status=status,
        adaptation_disposition=adaptation_disposition,
        orchestration_disposition=orchestration_disposition,
        integration_mode=integration_mode,
        historical_influence_applied=(historical_influence_applied),
        adaptation_applied=adaptation_applied,
        execution_authorized=execution_authorized,
        review_required=review_required,
        reason_count=10,
    )


def test_severity_values_are_stable() -> None:
    assert IntelligenceObservabilitySeverity.INFO.value == "info"
    assert IntelligenceObservabilitySeverity.NOTICE.value == "notice"
    assert IntelligenceObservabilitySeverity.WARNING.value == "warning"
    assert IntelligenceObservabilitySeverity.REVIEW.value == "review"


def test_builder_returns_observability_event() -> None:
    result = ObservabilityEventBuilder().build(make_summary())

    assert isinstance(
        result,
        IntelligenceObservabilityEvent,
    )


@pytest.mark.parametrize(
    "status,expected_severity,expected_code",
    [
        (
            IntelligenceObservabilityStatus.NORMAL,
            IntelligenceObservabilitySeverity.INFO,
            "INTELLIGENCE_NORMAL",
        ),
        (
            IntelligenceObservabilityStatus.ADVISORY,
            IntelligenceObservabilitySeverity.NOTICE,
            "INTELLIGENCE_ADVISORY",
        ),
        (
            IntelligenceObservabilityStatus.CONSTRAINED,
            IntelligenceObservabilitySeverity.WARNING,
            "INTELLIGENCE_CONSTRAINED",
        ),
        (
            IntelligenceObservabilityStatus.REVIEW_REQUIRED,
            IntelligenceObservabilitySeverity.REVIEW,
            "INTELLIGENCE_REVIEW_REQUIRED",
        ),
    ],
)
def test_complete_event_mapping(
    status: IntelligenceObservabilityStatus,
    expected_severity: IntelligenceObservabilitySeverity,
    expected_code: str,
) -> None:
    result = ObservabilityEventBuilder().build(
        make_summary(
            status=status,
        )
    )

    assert result.status is status
    assert result.severity is expected_severity
    assert result.diagnostic_code == expected_code


def test_normal_message_is_deterministic() -> None:
    result = ObservabilityEventBuilder().build(
        make_summary(
            status=IntelligenceObservabilityStatus.NORMAL,
        )
    )

    assert result.message == (
        "intelligence lifecycle completed with normal " "execution-preserving behavior"
    )


def test_advisory_message_is_deterministic() -> None:
    result = ObservabilityEventBuilder().build(
        make_summary(
            status=IntelligenceObservabilityStatus.ADVISORY,
        )
    )

    assert result.message == (
        "intelligence lifecycle includes advisory " "historical context"
    )


def test_constrained_message_is_deterministic() -> None:
    result = ObservabilityEventBuilder().build(
        make_summary(
            status=IntelligenceObservabilityStatus.CONSTRAINED,
        )
    )

    assert result.message == (
        "intelligence lifecycle requires approved " "bounded execution constraints"
    )


def test_review_message_is_deterministic() -> None:
    result = ObservabilityEventBuilder().build(
        make_summary(
            status=(IntelligenceObservabilityStatus.REVIEW_REQUIRED),
        )
    )

    assert result.message == (
        "intelligence lifecycle requires review-oriented " "handling"
    )


def test_builder_preserves_context_id() -> None:
    summary = make_summary()

    result = ObservabilityEventBuilder().build(summary)

    assert result.context_id == summary.context_id


def test_builder_preserves_correlation_id() -> None:
    summary = make_summary()

    result = ObservabilityEventBuilder().build(summary)

    assert result.correlation_id == summary.correlation_id


def test_builder_preserves_action() -> None:
    result = ObservabilityEventBuilder().build(
        make_summary(
            action=TaskAction.VERIFY,
        )
    )

    assert result.action is TaskAction.VERIFY


@pytest.mark.parametrize(
    "status",
    list(IntelligenceObservabilityStatus),
)
def test_lifecycle_state_is_preserved(
    status: IntelligenceObservabilityStatus,
) -> None:
    summary = make_summary(
        status=status,
    )

    result = ObservabilityEventBuilder().build(summary)

    assert result.historical_influence_applied is summary.historical_influence_applied
    assert result.adaptation_applied is summary.adaptation_applied
    assert result.execution_authorized is summary.execution_authorized
    assert result.review_required is summary.review_required


def test_reason_count_is_preserved() -> None:
    summary = make_summary()

    result = ObservabilityEventBuilder().build(summary)

    assert result.reason_count == summary.reason_count


def test_invalid_summary_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=("summary must be an " "IntelligenceObservabilitySummary"),
    ):
        ObservabilityEventBuilder().build("invalid")


def test_event_context_id_must_be_uuid() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="context_id must be a UUID",
    ):
        IntelligenceObservabilityEvent(
            context_id="invalid",
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=(summary.historical_influence_applied),
            adaptation_applied=summary.adaptation_applied,
            execution_authorized=summary.execution_authorized,
            review_required=summary.review_required,
            reason_count=summary.reason_count,
            diagnostic_code="TEST",
            message="test message",
        )


def test_event_correlation_id_must_be_uuid() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="correlation_id must be a UUID",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id="invalid",
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=(summary.historical_influence_applied),
            adaptation_applied=summary.adaptation_applied,
            execution_authorized=summary.execution_authorized,
            review_required=summary.review_required,
            reason_count=summary.reason_count,
            diagnostic_code="TEST",
            message="test message",
        )


def test_event_action_must_be_task_action() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="action must be a TaskAction",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action="summarize",
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=(summary.historical_influence_applied),
            adaptation_applied=summary.adaptation_applied,
            execution_authorized=summary.execution_authorized,
            review_required=summary.review_required,
            reason_count=summary.reason_count,
            diagnostic_code="TEST",
            message="test message",
        )


def test_event_status_must_be_valid() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match=("status must be an " "IntelligenceObservabilityStatus"),
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status="advisory",
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=10,
            diagnostic_code="TEST",
            message="test message",
        )


def test_event_severity_must_be_valid() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match=("severity must be an " "IntelligenceObservabilitySeverity"),
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity="notice",
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=10,
            diagnostic_code="TEST",
            message="test message",
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
def test_event_boolean_fields_require_bool(
    field_name: str,
) -> None:
    summary = make_summary()

    values = {
        "context_id": summary.context_id,
        "correlation_id": summary.correlation_id,
        "action": summary.action,
        "status": summary.status,
        "severity": IntelligenceObservabilitySeverity.NOTICE,
        "historical_influence_applied": True,
        "adaptation_applied": True,
        "execution_authorized": False,
        "review_required": False,
        "reason_count": 10,
        "diagnostic_code": "TEST",
        "message": "test message",
    }

    values[field_name] = 1

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        IntelligenceObservabilityEvent(**values)


def test_reason_count_must_be_integer() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="reason_count must be an integer",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=1.5,
            diagnostic_code="TEST",
            message="test message",
        )


def test_reason_count_rejects_bool() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="reason_count must be an integer",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=True,
            diagnostic_code="TEST",
            message="test message",
        )


def test_reason_count_must_be_non_negative() -> None:
    summary = make_summary()

    with pytest.raises(
        ValueError,
        match=("reason_count must be greater than or equal to 0"),
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=-1,
            diagnostic_code="TEST",
            message="test message",
        )


def test_diagnostic_code_must_be_string() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="diagnostic_code must be a string",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=10,
            diagnostic_code=123,
            message="test message",
        )


def test_diagnostic_code_must_not_be_empty() -> None:
    summary = make_summary()

    with pytest.raises(
        ValueError,
        match="diagnostic_code must not be empty",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=10,
            diagnostic_code="",
            message="test message",
        )


def test_message_must_be_string() -> None:
    summary = make_summary()

    with pytest.raises(
        TypeError,
        match="message must be a string",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=10,
            diagnostic_code="TEST",
            message=123,
        )


def test_message_must_not_be_empty() -> None:
    summary = make_summary()

    with pytest.raises(
        ValueError,
        match="message must not be empty",
    ):
        IntelligenceObservabilityEvent(
            context_id=summary.context_id,
            correlation_id=summary.correlation_id,
            action=summary.action,
            status=summary.status,
            severity=IntelligenceObservabilitySeverity.NOTICE,
            historical_influence_applied=True,
            adaptation_applied=True,
            execution_authorized=False,
            review_required=False,
            reason_count=10,
            diagnostic_code="TEST",
            message="",
        )


def test_event_is_frozen() -> None:
    result = ObservabilityEventBuilder().build(make_summary())

    with pytest.raises(FrozenInstanceError):
        result.message = "changed"


def test_event_uses_slots() -> None:
    result = ObservabilityEventBuilder().build(make_summary())

    assert not hasattr(result, "__dict__")


def test_builder_is_deterministic() -> None:
    summary = make_summary(
        status=IntelligenceObservabilityStatus.CONSTRAINED,
    )

    builder = ObservabilityEventBuilder()

    first = builder.build(summary)
    second = builder.build(summary)

    assert first == second


def test_builder_does_not_modify_summary() -> None:
    summary = make_summary()

    before = summary

    ObservabilityEventBuilder().build(summary)

    assert summary == before


def test_event_contains_no_timestamp() -> None:
    assert "timestamp" not in IntelligenceObservabilityEvent.__dataclass_fields__


def test_event_contains_no_runtime_configuration() -> None:
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

    assert not (forbidden & set(IntelligenceObservabilityEvent.__dataclass_fields__))


def test_event_contains_no_advanced_analytics() -> None:
    forbidden = {
        "score",
        "risk_score",
        "quality_score",
        "confidence_score",
        "success_probability",
        "risk_probability",
        "prediction",
    }

    assert not (forbidden & set(IntelligenceObservabilityEvent.__dataclass_fields__))


def test_builder_has_no_emit_interface() -> None:
    forbidden = {
        "emit",
        "publish",
        "send",
        "log",
        "record",
        "execute",
        "run",
    }

    public_names = {
        name for name in dir(ObservabilityEventBuilder) if not name.startswith("_")
    }

    assert not (forbidden & public_names)


def test_builder_exposes_only_build() -> None:
    public_names = {
        name for name in dir(ObservabilityEventBuilder) if not name.startswith("_")
    }

    assert public_names == {"build"}
