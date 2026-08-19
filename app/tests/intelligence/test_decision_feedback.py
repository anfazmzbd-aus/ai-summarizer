"""
Tests for the V10 DecisionFeedback contract.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.intelligence import (
    DecisionFeedback,
    PlannerOutcomeBuilder,
    StrategyPolicyHandoff,
    TaskAction,
    TaskDecision,
)
from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.planning import SummarizationPlanner
from app.summarization.strategies.models import (
    StrategySelectionConfig,
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


def make_context(constraints=None):
    from app.intelligence import IntelligenceContext

    return IntelligenceContext.create(
        request_id="m2-5-feedback",
        constraints={} if constraints is None else constraints,
    )


def make_outcome(constraints=None):
    context = make_context(constraints)

    decision = TaskDecision.create(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="feedback test",
        confidence=1.0,
        metadata={
            "request_id": context.request_id,
        },
    )

    from app.intelligence import (
        ConstraintAwarePlannerHandoff,
        PlannerHandoff,
    )

    handoff = StrategyPolicyHandoff(
        ConstraintAwarePlannerHandoff(PlannerHandoff(make_planner()))
    )

    result = handoff.execute(
        text="A short deterministic document.",
        context=context,
        decision=decision,
    )

    outcome = PlannerOutcomeBuilder().build(
        result=result,
        task_decision=decision,
    )

    return context, outcome


def test_feedback_can_be_created_from_outcome() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert isinstance(feedback, DecisionFeedback)


def test_feedback_preserves_context_id() -> None:
    context, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.context_id == context.context_id


def test_feedback_preserves_correlation_id() -> None:
    context, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.correlation_id == context.correlation_id


def test_feedback_preserves_selected_strategy() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.selected_strategy is outcome.selected_strategy


def test_feedback_preserves_decision_reason() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.decision_reason == outcome.decision_reason


def test_feedback_preserves_preference_result() -> None:
    _, outcome = make_outcome(
        {
            "preferred_strategy": "map_reduce",
        }
    )

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.preference_satisfied is False


def test_feedback_marks_hard_constraints_as_satisfied() -> None:
    _, outcome = make_outcome(
        {
            "allowed_strategies": ["direct"],
        }
    )

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.hard_constraints_satisfied is True


def test_feedback_preserves_constraint_summary() -> None:
    _, outcome = make_outcome(
        {
            "preferred_strategy": "direct",
            "allowed_strategies": ["direct", "map_reduce"],
        }
    )

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.constraint_summary == (
        "preferred_strategy=direct",
        "allowed_strategies=direct,map_reduce",
    )


def test_feedback_preserves_source_digest() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.source_digest == outcome.source_digest


def test_feedback_preserves_token_count() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.token_count == outcome.token_count


def test_feedback_preserves_chunk_count() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    assert feedback.chunk_count == outcome.chunk_count


def test_feedback_is_immutable() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(outcome)

    with pytest.raises(FrozenInstanceError):
        feedback.hard_constraints_satisfied = False  # type: ignore[misc]


def test_feedback_metadata_is_immutable() -> None:
    _, outcome = make_outcome()

    feedback = DecisionFeedback.from_outcome(
        outcome,
        metadata={"source": "test"},
    )

    with pytest.raises(TypeError):
        feedback.metadata["source"] = "changed"  # type: ignore[index]


def test_feedback_rejects_invalid_outcome() -> None:
    with pytest.raises(
        TypeError,
        match="outcome must be a PlannerOutcome",
    ):
        DecisionFeedback.from_outcome(None)  # type: ignore[arg-type]
