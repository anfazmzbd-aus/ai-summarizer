"""Focused tests for the V11 application-to-V10 integration boundary."""

from __future__ import annotations

from uuid import UUID

from app.core.application_contracts import SummarizationApplicationRequest
from app.core.intelligence_integration import ApplicationIntelligenceBoundary


def test_application_boundary_returns_validated_execution_neutral_result() -> None:
    result = ApplicationIntelligenceBoundary().evaluate(
        SummarizationApplicationRequest(text="A short document.")
    )

    assert isinstance(result.context_id, UUID)
    assert isinstance(result.correlation_id, UUID)
    assert result.action == "summarize"
    assert result.mode == "preserve"
    assert result.execution_change_authorized is False
    assert result.bounded_constraint_required is False
    assert result.review_required is False
    assert "existing execution behavior remains unchanged" in result.reasons


def test_application_boundary_does_not_expose_v10_or_runtime_objects() -> None:
    result = ApplicationIntelligenceBoundary().evaluate(
        SummarizationApplicationRequest(
            text="A document.",
            provider="fake",
            model="test-model",
        )
    )

    assert not hasattr(result, "provider")
    assert not hasattr(result, "model")
    assert not hasattr(result, "runtime")
    assert not hasattr(result, "handoff")


def test_application_boundary_preserves_v10_provenance_across_projection() -> None:
    result = ApplicationIntelligenceBoundary().evaluate(
        SummarizationApplicationRequest(text="A document.")
    )

    assert result.context_id != result.correlation_id
    assert result.context_id is not None
    assert result.correlation_id is not None
