"""V10 production-boundary validation tests.

These tests verify that the V10 intelligence contracts compose correctly
with existing V9.3 intelligence artifacts and remain independent from the
existing runtime/application implementation.

No production runtime integration is performed in M1.7.
"""

from __future__ import annotations

from uuid import uuid4

from app.intelligence import (
    ExecutionMode,
    IntelligenceContext,
    ProvenanceContext,
    RuntimeDecision,
    TaskAction,
    TaskDecision,
)
from app.summarization.intelligence import (
    DocumentProfiler,
    IntentClassifier,
    SummarizationIntent,
)


def test_v9_document_profile_can_populate_v10_context() -> None:
    text = """
    # Technical deployment

    The API architecture was updated.
    Configuration and deployment procedures changed.
    """

    profile = DocumentProfiler().profile(text)

    context = IntelligenceContext(
        document_profile=profile,
    )

    assert context.document_profile is profile
    assert context.document_profile is not None
    assert context.document_profile.token_count > 0


def test_v9_intent_classification_can_populate_v10_context() -> None:
    text = "The API deployment architecture and configuration " "changed significantly."

    classification = IntentClassifier().classify(text)

    context = IntelligenceContext(
        intent_classification=classification,
    )

    assert context.intent_classification is classification
    assert context.intent is classification.intent
    assert classification.intent is SummarizationIntent.TECHNICAL


def test_v9_document_and_intent_intelligence_compose_in_v10_context() -> None:
    text = """
    # Technical deployment

    The API deployment architecture changed.
    The configuration requires validation.
    """

    profile = DocumentProfiler().profile(text)
    classification = IntentClassifier().classify(text)

    context = IntelligenceContext(
        document_profile=profile,
        intent_classification=classification,
    )

    assert context.document_profile is profile
    assert context.intent_classification is classification
    assert context.document_profile.token_count > 0
    assert context.intent is classification.intent


def test_v10_context_can_drive_a_task_decision() -> None:
    context = IntelligenceContext(
        request_id="req-001",
    )

    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="V9.3 document is eligible for summarization",
        confidence=0.95,
    )

    assert decision.action is TaskAction.SUMMARIZE
    assert decision.context_id == context.context_id
    assert decision.correlation_id == context.correlation_id
    assert decision.confidence == 0.95


def test_v10_task_decision_can_produce_runtime_decision() -> None:
    context = IntelligenceContext(
        request_id="req-002",
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=task_decision.context_id,
        correlation_id=task_decision.correlation_id,
    )

    assert runtime_decision.context_id == task_decision.context_id
    assert runtime_decision.correlation_id == task_decision.correlation_id


def test_complete_v10_boundary_preserves_single_correlation_identity() -> None:
    correlation_id = uuid4()

    provenance = ProvenanceContext(
        correlation_id=correlation_id,
    )

    context = IntelligenceContext(
        correlation_id=provenance.correlation_id,
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context.context_id,
        correlation_id=task_decision.correlation_id,
    )

    assert provenance.correlation_id == correlation_id
    assert context.correlation_id == correlation_id
    assert task_decision.correlation_id == correlation_id
    assert runtime_decision.correlation_id == correlation_id


def test_existing_execution_id_can_be_attached_without_replacing_correlation_id() -> (
    None
):
    correlation_id = uuid4()
    execution_id = uuid4()

    provenance = ProvenanceContext(
        correlation_id=correlation_id,
        execution_id=execution_id,
    )

    assert provenance.correlation_id == correlation_id
    assert provenance.execution_id == execution_id
    assert provenance.correlation_id != provenance.execution_id


def test_v10_boundary_can_reference_a_future_plan_id() -> None:
    context_id = uuid4()
    correlation_id = uuid4()
    plan_id = uuid4()

    provenance = ProvenanceContext(
        context_id=context_id,
        correlation_id=correlation_id,
        plan_id=plan_id,
    )

    decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert provenance.plan_id == plan_id
    assert decision.context_id == context_id
    assert runtime_decision.context_id == context_id


def test_v10_boundary_does_not_require_a_provider() -> None:
    context = IntelligenceContext(
        request_id="provider-independent",
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    provenance = ProvenanceContext(
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    for artifact in (
        context,
        task_decision,
        runtime_decision,
        provenance,
    ):
        assert not hasattr(artifact, "provider")
        assert not hasattr(artifact, "client")
        assert not hasattr(artifact, "llm_service")


def test_v10_boundary_does_not_require_runtime_objects() -> None:
    context = IntelligenceContext()

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    provenance = ProvenanceContext(
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    for artifact in (
        context,
        task_decision,
        runtime_decision,
        provenance,
    ):
        assert not hasattr(artifact, "runtime")
        assert not hasattr(artifact, "execution_engine")
        assert not hasattr(artifact, "executor")
        assert not hasattr(artifact, "scheduler")


def test_v10_boundary_preserves_v9_deterministic_intelligence() -> None:
    text = "The API deployment architecture and configuration changed."

    first_profile = DocumentProfiler().profile(text)
    second_profile = DocumentProfiler().profile(text)

    first_intent = IntentClassifier().classify(text)
    second_intent = IntentClassifier().classify(text)

    assert first_profile == second_profile
    assert first_intent == second_intent

    first_context = IntelligenceContext(
        document_profile=first_profile,
        intent_classification=first_intent,
    )

    second_context = IntelligenceContext(
        document_profile=second_profile,
        intent_classification=second_intent,
    )

    assert first_context.document_profile == second_context.document_profile
    assert first_context.intent_classification == (second_context.intent_classification)


def test_v10_contracts_are_application_boundary_artifacts_only() -> None:
    context = IntelligenceContext()

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    assert task_decision.action is TaskAction.SUMMARIZE
    assert runtime_decision.mode is ExecutionMode.SEQUENTIAL

    assert not hasattr(context, "run")
    assert not hasattr(task_decision, "run")
    assert not hasattr(runtime_decision, "run")


def test_provenance_serialization_exposes_complete_boundary_identity() -> None:
    context_id = uuid4()
    correlation_id = uuid4()
    task_decision_id = uuid4()
    plan_id = uuid4()
    execution_id = uuid4()

    provenance = ProvenanceContext(
        context_id=context_id,
        correlation_id=correlation_id,
        task_decision_id=task_decision_id,
        plan_id=plan_id,
        execution_id=execution_id,
    )

    payload = provenance.to_dict()

    assert payload["context_id"] == str(context_id)
    assert payload["correlation_id"] == str(correlation_id)
    assert payload["task_decision_id"] == str(task_decision_id)
    assert payload["plan_id"] == str(plan_id)
    assert payload["execution_id"] == str(execution_id)


def test_nested_v10_lifecycle_preserves_parent_lineage() -> None:
    parent = ProvenanceContext.create()

    child = ProvenanceContext.create(
        parent_correlation_id=parent.correlation_id,
    )

    context = IntelligenceContext(
        correlation_id=child.correlation_id,
    )

    decision = TaskDecision(
        action=TaskAction.REFINE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    assert child.parent_correlation_id == parent.correlation_id
    assert context.correlation_id == child.correlation_id
    assert decision.correlation_id == child.correlation_id


def test_v9_summarization_intelligence_remains_owned_by_v9_domain() -> None:
    text = "The research study reports new findings and evidence."

    classification = IntentClassifier().classify(text)

    assert classification.intent is SummarizationIntent.FINDINGS

    context = IntelligenceContext(
        intent_classification=classification,
    )

    assert context.intent is SummarizationIntent.FINDINGS

    # The V10 context contains the V9-derived result. It does not own
    # or replace the V9 classifier.
    assert not hasattr(context, "classify")
    assert not hasattr(context, "profile")


def test_v10_runtime_decision_remains_declarative() -> None:
    context = IntelligenceContext()

    decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        timeout_seconds=30.0,
        retry_enabled=True,
        max_retry_attempts=2,
        fallback_allowed=True,
    )

    assert decision.mode is ExecutionMode.SEQUENTIAL
    assert decision.timeout_seconds == 30.0
    assert decision.retry_enabled is True
    assert decision.max_retry_attempts == 2
    assert decision.fallback_allowed is True

    assert not hasattr(decision, "execute")
    assert not hasattr(decision, "run")
    assert not hasattr(decision, "retry")


def test_production_boundary_does_not_mutate_v9_artifacts() -> None:
    text = "The API architecture changed."

    profile = DocumentProfiler().profile(text)
    classification = IntentClassifier().classify(text)

    original_profile = profile
    original_classification = classification

    context = IntelligenceContext(
        document_profile=profile,
        intent_classification=classification,
    )

    TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    assert context.document_profile is original_profile
    assert context.intent_classification is original_classification
