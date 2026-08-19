"""
Tests for the V10 IntelligenceOrchestrator.
"""

from __future__ import annotations

import pytest

from app.intelligence import (
    IntelligenceContext,
    IntelligenceOrchestrator,
    TaskAction,
)
from app.summarization.intelligence import (
    IntentClassification,
    SummarizationIntent,
)


def make_context(
    *,
    intent: SummarizationIntent | None = None,
    constraints: dict | None = None,
) -> IntelligenceContext:
    classification = None

    if intent is not None:
        classification = IntentClassification(
            intent=intent,
            confidence=1.0,
            scores={intent: 1.0},
            explicit=True,
        )

    return IntelligenceContext.create(
        request_id="m2-test",
        intent_classification=classification,
        constraints=constraints or {},
    )


def test_orchestrator_defaults_to_summarization() -> None:
    context = make_context()

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.SUMMARIZE
    assert decision.context_id == context.context_id
    assert decision.correlation_id == context.correlation_id


@pytest.mark.parametrize(
    "intent",
    [
        SummarizationIntent.GENERAL,
        SummarizationIntent.EXECUTIVE,
        SummarizationIntent.ACTION_ITEMS,
        SummarizationIntent.KEY_POINTS,
        SummarizationIntent.FINDINGS,
        SummarizationIntent.INSIGHTS,
        SummarizationIntent.TECHNICAL,
    ],
)
def test_supported_summarization_intents_produce_summarize_action(
    intent: SummarizationIntent,
) -> None:
    context = make_context(intent=intent)

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.SUMMARIZE
    assert decision.confidence == 1.0


@pytest.mark.parametrize(
    ("constraint", "expected_action"),
    [
        ("abort", TaskAction.ABORT),
        ("retry", TaskAction.RETRY),
        ("fallback", TaskAction.FALLBACK),
        ("verify", TaskAction.VERIFY),
        ("retrieve", TaskAction.RETRIEVE),
        ("refine", TaskAction.REFINE),
    ],
)
def test_constraints_control_task_action(
    constraint: str,
    expected_action: TaskAction,
) -> None:
    context = make_context(
        constraints={constraint: True},
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is expected_action
    assert decision.confidence == 1.0


def test_constraint_has_precedence_over_intent() -> None:
    context = make_context(
        intent=SummarizationIntent.TECHNICAL,
        constraints={"verify": True},
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.VERIFY
    assert decision.reason == "verification requested by constraint"


def test_abort_has_highest_constraint_precedence() -> None:
    context = make_context(
        constraints={
            "abort": True,
            "retry": True,
            "fallback": True,
            "verify": True,
        },
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.ABORT


def test_retry_precedes_fallback() -> None:
    context = make_context(
        constraints={
            "retry": True,
            "fallback": True,
        },
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.RETRY


def test_fallback_precedes_verify() -> None:
    context = make_context(
        constraints={
            "fallback": True,
            "verify": True,
        },
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.FALLBACK


def test_verify_precedes_retrieve() -> None:
    context = make_context(
        constraints={
            "verify": True,
            "retrieve": True,
        },
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.VERIFY


def test_orchestrator_preserves_provenance() -> None:
    context = make_context(
        intent=SummarizationIntent.TECHNICAL,
    )

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.context_id == context.context_id
    assert decision.correlation_id == context.correlation_id


def test_orchestrator_is_deterministic_for_same_context() -> None:
    context = make_context(
        intent=SummarizationIntent.FINDINGS,
    )

    orchestrator = IntelligenceOrchestrator()

    first = orchestrator.decide(context)
    second = orchestrator.decide(context)

    assert first == second


def test_orchestrator_does_not_execute_tasks() -> None:
    orchestrator = IntelligenceOrchestrator()

    assert not hasattr(orchestrator, "execute")
    assert not hasattr(orchestrator, "run")
    assert not hasattr(orchestrator, "retry")


def test_orchestrator_has_no_provider_dependency() -> None:
    orchestrator = IntelligenceOrchestrator()

    assert not hasattr(orchestrator, "provider")
    assert not hasattr(orchestrator, "client")
    assert not hasattr(orchestrator, "llm_service")


def test_invalid_context_is_rejected() -> None:
    with pytest.raises(TypeError, match="context must be an IntelligenceContext"):
        IntelligenceOrchestrator().decide("invalid")  # type: ignore[arg-type]


def test_unknown_intent_falls_back_to_summarization() -> None:
    context = IntelligenceContext.create()

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.action is TaskAction.SUMMARIZE


def test_reason_explains_default_decision() -> None:
    context = make_context()

    decision = IntelligenceOrchestrator().decide(context)

    assert decision.reason
    assert "default" in decision.reason
