"""
Tests for the V10 PlannerOutcome contract.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    PlannerOutcome,
    PlannerOutcomeBuilder,
    StrategyPolicyHandoff,
    TaskAction,
    TaskDecision,
)
from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.planning import SummarizationPlanner
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


def make_planner() -> SummarizationPlanner:
    return SummarizationPlanner(
        chunker=TextChunker(
            ChunkingConfig(
                max_tokens=100,
                overlap_tokens=0,
                preserve_boundaries=False,
            )
        ),
        selector=SummarizationStrategySelector(
            StrategySelectionConfig(
                direct_max_tokens=2_000,
                map_reduce_max_tokens=10_000,
            )
        ),
    )


def make_context(constraints: dict | None = None):
    from app.intelligence import IntelligenceContext

    return IntelligenceContext.create(
        request_id="m2-5-test",
        constraints=constraints or {},
    )


def make_decision(context) -> TaskDecision:
    return TaskDecision.create(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="planner outcome test",
        confidence=1.0,
        metadata={
            "request_id": context.request_id,
        },
    )


def make_result(
    *,
    text: str = "A short deterministic document.",
    constraints: dict | None = None,
):
    context = make_context(constraints)

    handoff = StrategyPolicyHandoff(
        __import__(
            "app.intelligence",
            fromlist=["ConstraintAwarePlannerHandoff"],
        ).ConstraintAwarePlannerHandoff(
            __import__(
                "app.intelligence",
                fromlist=["PlannerHandoff"],
            ).PlannerHandoff(make_planner())
        )
    )

    result = handoff.execute(
        text=text,
        context=context,
        decision=make_decision(context),
    )

    return context, result


def test_builder_creates_planner_outcome() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert isinstance(outcome, PlannerOutcome)
    assert outcome.plan is result.plan
    assert outcome.selected_strategy is result.selected_strategy


def test_outcome_preserves_plan_identity() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.plan is result.plan


def test_outcome_exposes_context_id() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.context_id == context.context_id


def test_outcome_exposes_correlation_id() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.correlation_id == context.correlation_id


def test_outcome_exposes_selected_strategy() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.selected_strategy is result.selected_strategy
    assert outcome.selected_strategy is outcome.plan.strategy


def test_outcome_preserves_preference_result() -> None:
    context, result = make_result(
        constraints={
            "preferred_strategy": "map_reduce",
        }
    )

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.preference_satisfied is False
    assert outcome.preference_overridden is True


def test_outcome_preserves_preference_success() -> None:
    context, result = make_result(
        constraints={
            "preferred_strategy": "direct",
        }
    )

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.preference_satisfied is True
    assert outcome.preference_overridden is False


def test_outcome_exposes_planner_metadata() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.planner_metadata["planner_version"] == (
        result.plan.metadata["planner_version"]
    )


def test_outcome_exposes_source_digest() -> None:
    context, result = make_result(
        text="A deterministic source document.",
    )

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.source_digest == result.plan.source_digest


def test_outcome_exposes_token_count() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.token_count == result.plan.token_count


def test_outcome_exposes_chunk_count() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.chunk_count == result.plan.chunk_count


def test_outcome_contains_constraint_summary() -> None:
    context, result = make_result(
        constraints={
            "preferred_strategy": "direct",
            "allowed_strategies": ["direct", "map_reduce"],
        }
    )

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.constraint_summary == (
        "preferred_strategy=direct",
        "allowed_strategies=direct,map_reduce",
    )


def test_outcome_uses_strategy_reason_as_decision_reason() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    assert outcome.decision_reason == result.plan.metadata["strategy_reason"]


def test_outcome_is_immutable() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
    )

    with pytest.raises(FrozenInstanceError):
        outcome.selected_strategy = SummarizationStrategyType.MAP_REDUCE  # type: ignore[misc]


def test_outcome_metadata_is_immutable() -> None:
    context, result = make_result()

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=make_decision(context),
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        outcome.metadata["source"] = "changed"  # type: ignore[index]


def test_builder_rejects_invalid_result() -> None:
    context = make_context()

    with pytest.raises(
        TypeError,
        match="result must be a StrategyPolicyResult",
    ):
        PlannerOutcomeBuilder().build(
            result=None,  # type: ignore[arg-type]
            task_decision=make_decision(context),
        )


def test_builder_rejects_invalid_task_decision() -> None:
    _, result = make_result()

    with pytest.raises(
        TypeError,
        match="task_decision must be a TaskDecision",
    ):
        PlannerOutcomeBuilder().build(
            result=result,
            task_decision=None,  # type: ignore[arg-type]
        )


def test_outcome_rejects_mismatched_selected_strategy() -> None:
    context, result = make_result()
    task_decision = make_decision(context)

    with pytest.raises(
        ValueError,
        match="selected_strategy must match plan.strategy",
    ):
        PlannerOutcome(
            plan=result.plan,
            task_decision=task_decision,
            strategy_policy_result=result,
            selected_strategy=SummarizationStrategyType.MAP_REDUCE,
            decision_reason="invalid",
        )
