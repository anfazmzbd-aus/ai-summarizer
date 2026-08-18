"""Integration tests for the V10 intelligence architecture contracts."""

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


def test_v10_contracts_form_a_complete_decision_chain() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    provenance = ProvenanceContext(
        correlation_id=correlation_id,
        context_id=context_id,
    )

    context = IntelligenceContext(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=provenance.correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context.context_id,
        correlation_id=provenance.correlation_id,
    )

    assert context.context_id == context_id
    assert task_decision.context_id == context_id
    assert runtime_decision.context_id == context_id

    assert task_decision.correlation_id == correlation_id
    assert runtime_decision.correlation_id == correlation_id


def test_provenance_can_correlate_task_and_runtime_decisions() -> None:
    context_id = uuid4()
    correlation_id = uuid4()
    task_decision_id = uuid4()
    execution_id = uuid4()

    provenance = ProvenanceContext(
        correlation_id=correlation_id,
        context_id=context_id,
        task_decision_id=task_decision_id,
        execution_id=execution_id,
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert provenance.correlation_id == task_decision.correlation_id
    assert provenance.correlation_id == runtime_decision.correlation_id
    assert provenance.task_decision_id == task_decision_id
    assert provenance.execution_id == execution_id


def test_context_and_decisions_share_the_same_lifecycle_identity() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    context = IntelligenceContext(
        context_id=context_id,
        correlation_id=correlation_id,
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

    assert {
        context.correlation_id,
        task_decision.correlation_id,
        runtime_decision.correlation_id,
    } == {correlation_id}

    assert {
        context.context_id,
        task_decision.context_id,
        runtime_decision.context_id,
    } == {context_id}


def test_task_and_runtime_decisions_remain_separate_contracts() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert task_decision.action is TaskAction.SUMMARIZE
    assert runtime_decision.mode is ExecutionMode.SEQUENTIAL

    assert not hasattr(task_decision, "timeout_seconds")
    assert not hasattr(runtime_decision, "action")


def test_provenance_supports_future_evaluation_and_adaptation() -> None:
    correlation_id = uuid4()

    evaluation_id = uuid4()
    adaptation_id = uuid4()

    provenance = ProvenanceContext(
        correlation_id=correlation_id,
        evaluation_id=evaluation_id,
        adaptation_id=adaptation_id,
    )

    assert provenance.correlation_id == correlation_id
    assert provenance.evaluation_id == evaluation_id
    assert provenance.adaptation_id == adaptation_id


def test_nested_lifecycle_preserves_parent_correlation() -> None:
    parent = ProvenanceContext.create()

    child = ProvenanceContext.create(
        parent_correlation_id=parent.correlation_id,
    )

    context = IntelligenceContext(
        correlation_id=child.correlation_id,
        context_id=uuid4(),
    )

    decision = TaskDecision(
        action=TaskAction.REFINE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
    )

    assert child.parent_correlation_id == parent.correlation_id
    assert context.correlation_id == child.correlation_id
    assert decision.correlation_id == child.correlation_id


def test_v10_contracts_do_not_depend_on_provider_objects() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    context = IntelligenceContext(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    provenance = ProvenanceContext(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    for artifact in (
        context,
        task_decision,
        runtime_decision,
        provenance,
    ):
        assert not hasattr(artifact, "provider")
        assert not hasattr(artifact, "client")
        assert not hasattr(artifact, "executor")


def test_v10_contracts_are_immutable() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    context = IntelligenceContext(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    task_decision = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    runtime_decision = RuntimeDecision(
        mode=ExecutionMode.SEQUENTIAL,
        context_id=context_id,
        correlation_id=correlation_id,
    )

    provenance = ProvenanceContext(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    assert context.__dataclass_params__.frozen
    assert task_decision.__dataclass_params__.frozen
    assert runtime_decision.__dataclass_params__.frozen
    assert provenance.__dataclass_params__.frozen


def test_provenance_serialization_preserves_correlation_chain() -> None:
    context_id = uuid4()
    correlation_id = uuid4()
    execution_id = uuid4()

    provenance = ProvenanceContext(
        correlation_id=correlation_id,
        context_id=context_id,
        execution_id=execution_id,
    )

    payload = provenance.to_dict()

    assert payload["correlation_id"] == str(correlation_id)
    assert payload["context_id"] == str(context_id)
    assert payload["execution_id"] == str(execution_id)


def test_complete_chain_is_deterministic_for_fixed_inputs() -> None:
    context_id = uuid4()
    correlation_id = uuid4()

    context = IntelligenceContext(
        context_id=context_id,
        correlation_id=correlation_id,
    )

    first = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="deterministic planning",
        confidence=0.9,
    )

    second = TaskDecision(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="deterministic planning",
        confidence=0.9,
    )

    assert first == second
