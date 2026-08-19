"""
Complete tests for the V10 planner handoff boundary.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.intelligence import (
    IntelligenceContext,
    PlannerHandoff,
    PlannerHandoffResult,
    TaskAction,
    TaskDecision,
)
from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.intelligence import SummarizationIntent
from app.summarization.planning import SummarizationPlan, SummarizationPlanner
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import SummarizationStrategySelector


def make_planner(
    *,
    max_tokens: int = 512,
    direct_max_tokens: int = 2_000,
    map_reduce_max_tokens: int = 10_000,
) -> SummarizationPlanner:
    """Create a deterministic V9.3 planner for tests."""
    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=max_tokens,
            overlap_tokens=0,
            preserve_boundaries=False,
        )
    )

    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=direct_max_tokens,
            map_reduce_max_tokens=map_reduce_max_tokens,
        )
    )

    return SummarizationPlanner(
        chunker=chunker,
        selector=selector,
    )


def make_context(
    *,
    intent: SummarizationIntent | None = None,
) -> IntelligenceContext:
    """Create a deterministic V10 context for tests."""
    classification = None

    if intent is not None:
        from app.summarization.intelligence import IntentClassification

        classification = IntentClassification(
            intent=intent,
            confidence=1.0,
            scores={intent: 1.0},
            explicit=True,
        )

    return IntelligenceContext.create(
        request_id="m2-2-test",
        intent_classification=classification,
    )


def make_decision(
    context: IntelligenceContext,
    *,
    action: TaskAction = TaskAction.SUMMARIZE,
) -> TaskDecision:
    """Create a decision aligned with the supplied context."""
    return TaskDecision.create(
        action=action,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="test decision",
        confidence=1.0,
    )


def test_handoff_returns_v9_plan() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert isinstance(result, PlannerHandoffResult)
    assert isinstance(result.plan, SummarizationPlan)


def test_handoff_preserves_context_id() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.context_id == context.context_id


def test_handoff_preserves_correlation_id() -> None:
    correlation_id = uuid4()

    context = IntelligenceContext.create(
        correlation_id=correlation_id,
    )

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.correlation_id == correlation_id


def test_handoff_preserves_both_provenance_identifiers() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.context_id == context.context_id
    assert result.correlation_id == context.correlation_id


def test_handoff_provenance_is_serializable() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.provenance == {
        "context_id": str(context.context_id),
        "correlation_id": str(context.correlation_id),
    }


def test_handoff_passes_explicit_intent_to_v9_planner() -> None:
    context = make_context(
        intent=SummarizationIntent.TECHNICAL,
    )

    result = PlannerHandoff(make_planner()).handoff(
        text="The API deployment configuration changed.",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.intent is SummarizationIntent.TECHNICAL
    assert result.plan.intent_classification is not None
    assert result.plan.intent_classification.explicit is True


def test_handoff_allows_v9_planner_to_infer_intent() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="The team must follow up with the customer.",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.intent is SummarizationIntent.ACTION_ITEMS


def test_handoff_preserves_existing_strategy_selection() -> None:
    context = make_context()

    planner = make_planner(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=5,
    )

    result = PlannerHandoff(planner).handoff(
        text="one two three four",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.strategy is SummarizationStrategyType.MAP_REDUCE
    assert result.plan.selection.strategy is (SummarizationStrategyType.MAP_REDUCE)


def test_handoff_does_not_replace_v9_planner() -> None:
    planner = make_planner()
    handoff = PlannerHandoff(planner)

    assert handoff.planner is planner


def test_handoff_does_not_modify_v9_plan() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert "context_id" not in result.plan.metadata
    assert "correlation_id" not in result.plan.metadata


def test_handoff_rejects_non_string_text() -> None:
    context = make_context()

    with pytest.raises(TypeError, match="text must be a string"):
        PlannerHandoff(make_planner()).handoff(
            text=123,  # type: ignore[arg-type]
            context=context,
            decision=make_decision(context),
        )


def test_handoff_rejects_invalid_context() -> None:
    with pytest.raises(
        TypeError,
        match="context must be an IntelligenceContext",
    ):
        PlannerHandoff(make_planner()).handoff(
            text="one two",
            context=object(),  # type: ignore[arg-type]
            decision=object(),  # type: ignore[arg-type]
        )


def test_handoff_rejects_invalid_decision() -> None:
    context = make_context()

    with pytest.raises(
        TypeError,
        match="decision must be a TaskDecision",
    ):
        PlannerHandoff(make_planner()).handoff(
            text="one two",
            context=context,
            decision=object(),  # type: ignore[arg-type]
        )


def test_handoff_rejects_context_id_mismatch() -> None:
    context = make_context()

    decision = TaskDecision.create(
        action=TaskAction.SUMMARIZE,
        context_id=uuid4(),
        correlation_id=context.correlation_id,
    )

    with pytest.raises(
        ValueError,
        match="context_id does not match",
    ):
        PlannerHandoff(make_planner()).handoff(
            text="one two",
            context=context,
            decision=decision,
        )


def test_handoff_rejects_correlation_id_mismatch() -> None:
    context = make_context()

    decision = TaskDecision.create(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=uuid4(),
    )

    with pytest.raises(
        ValueError,
        match="correlation_id does not match",
    ):
        PlannerHandoff(make_planner()).handoff(
            text="one two",
            context=context,
            decision=decision,
        )


@pytest.mark.parametrize(
    "action",
    [
        TaskAction.RETRIEVE,
        TaskAction.VERIFY,
        TaskAction.REFINE,
        TaskAction.RETRY,
        TaskAction.FALLBACK,
        TaskAction.ABORT,
    ],
)
def test_non_summarization_actions_are_not_sent_to_v9_planner(
    action: TaskAction,
) -> None:
    context = make_context()

    decision = make_decision(
        context,
        action=action,
    )

    with pytest.raises(
        ValueError,
        match="only TaskAction.SUMMARIZE",
    ):
        PlannerHandoff(make_planner()).handoff(
            text="one two three",
            context=context,
            decision=decision,
        )


def test_handoff_rejects_invalid_planner() -> None:
    with pytest.raises(
        TypeError,
        match="planner must be a SummarizationPlanner",
    ):
        PlannerHandoff(object())  # type: ignore[arg-type]


def test_handoff_is_deterministic_for_same_inputs() -> None:
    text = "The API deployment architecture changed."

    context = make_context(
        intent=SummarizationIntent.TECHNICAL,
    )

    decision = make_decision(context)

    planner = make_planner()
    handoff = PlannerHandoff(planner)

    first = handoff.handoff(
        text=text,
        context=context,
        decision=decision,
    )

    second = handoff.handoff(
        text=text,
        context=context,
        decision=decision,
    )

    assert first.plan == second.plan
    assert first.context_id == second.context_id
    assert first.correlation_id == second.correlation_id


def test_handoff_preserves_source_provenance_from_v9_plan() -> None:
    text = "The API deployment architecture changed."

    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text=text,
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.source_character_count == len(text)
    assert result.plan.source_digest


def test_handoff_does_not_execute_summarization() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert isinstance(result.plan, SummarizationPlan)
    assert not hasattr(result, "summary")
    assert not hasattr(result, "execution")
    assert not hasattr(result, "provider")


def test_handoff_result_is_immutable() -> None:
    context = make_context()

    result = PlannerHandoff(make_planner()).handoff(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    with pytest.raises(AttributeError):
        result.context_id = uuid4()  # type: ignore[misc]
