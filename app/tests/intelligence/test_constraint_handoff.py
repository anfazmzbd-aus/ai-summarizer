"""
Complete tests for the V10 constraint-aware planner handoff.
"""

from __future__ import annotations

import pytest

from app.intelligence import (
    ConstraintAwarePlannerHandoff,
    IntelligenceContext,
    PlannerHandoff,
    TaskAction,
    TaskDecision,
)
from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.intelligence import (
    DocumentProfile,
    DocumentStructureType,
    SummarizationIntent,
)
from app.summarization.planning import SummarizationPlanner
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import SummarizationStrategySelector


def make_profile(
    *,
    token_count: int = 10,
) -> DocumentProfile:
    return DocumentProfile(
        character_count=50,
        token_count=token_count,
        word_count=10,
        unique_word_count=8,
        paragraph_count=1,
        sentence_count=2,
        heading_count=0,
        list_item_count=0,
        code_block_count=0,
        quote_block_count=0,
        table_row_count=0,
        average_sentence_tokens=5.0,
        lexical_diversity=0.8,
        structure_type=DocumentStructureType.PROSE,
    )


def make_planner(
    *,
    max_tokens: int = 3,
    direct_max_tokens: int = 2_000,
    map_reduce_max_tokens: int = 10_000,
) -> SummarizationPlanner:
    return SummarizationPlanner(
        chunker=TextChunker(
            ChunkingConfig(
                max_tokens=max_tokens,
                overlap_tokens=0,
                preserve_boundaries=False,
            )
        ),
        selector=SummarizationStrategySelector(
            StrategySelectionConfig(
                direct_max_tokens=direct_max_tokens,
                map_reduce_max_tokens=map_reduce_max_tokens,
            )
        ),
    )


def make_context(
    *,
    constraints: dict | None = None,
    profile: DocumentProfile | None = None,
    intent: SummarizationIntent | None = None,
) -> IntelligenceContext:
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
        request_id="m2-3-test",
        document_profile=profile,
        intent_classification=classification,
        constraints=constraints or {},
    )


def make_decision(
    context: IntelligenceContext,
) -> TaskDecision:
    return TaskDecision.create(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="test decision",
        confidence=1.0,
    )


def make_handoff(
    planner: SummarizationPlanner | None = None,
) -> ConstraintAwarePlannerHandoff:
    return ConstraintAwarePlannerHandoff(PlannerHandoff(planner or make_planner()))


def test_unconstrained_handoff_succeeds() -> None:
    context = make_context()
    decision = make_decision(context)

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=decision,
    )

    assert result.plan.chunk_count == 1


def test_max_input_tokens_allows_document_within_limit() -> None:
    context = make_context(
        profile=make_profile(token_count=10),
        constraints={"max_input_tokens": 10},
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan


def test_max_input_tokens_rejects_document_over_limit() -> None:
    context = make_context(
        profile=make_profile(token_count=11),
        constraints={"max_input_tokens": 10},
    )

    with pytest.raises(
        ValueError,
        match="document token count exceeds max_input_tokens",
    ):
        make_handoff().execute(
            text="one two three",
            context=context,
            decision=make_decision(context),
        )


def test_max_input_tokens_is_also_checked_against_plan() -> None:
    context = make_context(
        constraints={"max_input_tokens": 1},
    )

    with pytest.raises(
        ValueError,
        match="plan token count exceeds max_input_tokens",
    ):
        make_handoff().execute(
            text="one two three",
            context=context,
            decision=make_decision(context),
        )


def test_max_chunks_allows_plan_within_limit() -> None:
    context = make_context(
        constraints={"max_chunks": 2},
    )

    result = make_handoff(
        make_planner(max_tokens=10),
    ).execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.chunk_count <= 2


def test_max_chunks_rejects_plan_over_limit() -> None:
    context = make_context(
        constraints={"max_chunks": 1},
    )

    with pytest.raises(
        ValueError,
        match="plan chunk count exceeds max_chunks",
    ):
        make_handoff(
            make_planner(max_tokens=1),
        ).execute(
            text="one two three four five",
            context=context,
            decision=make_decision(context),
        )


def test_allowed_strategies_accepts_selected_strategy() -> None:
    context = make_context(
        constraints={
            "allowed_strategies": ["direct"],
        }
    )

    result = make_handoff(
        make_planner(
            max_tokens=100,
            direct_max_tokens=2_000,
            map_reduce_max_tokens=10_000,
        )
    ).execute(
        text="one two",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.strategy is SummarizationStrategyType.DIRECT


def test_allowed_strategies_rejects_selected_strategy() -> None:
    context = make_context(
        constraints={
            "allowed_strategies": ["map_reduce"],
        }
    )

    with pytest.raises(
        ValueError,
        match="selected strategy 'direct' is not allowed",
    ):
        make_handoff(
            make_planner(
                max_tokens=100,
                direct_max_tokens=2_000,
                map_reduce_max_tokens=10_000,
            )
        ).execute(
            text="one two",
            context=context,
            decision=make_decision(context),
        )


def test_required_strategy_accepts_matching_strategy() -> None:
    context = make_context(
        constraints={
            "required_strategy": "direct",
        }
    )

    result = make_handoff(
        make_planner(
            max_tokens=100,
            direct_max_tokens=2_000,
        )
    ).execute(
        text="one two",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.strategy is SummarizationStrategyType.DIRECT


def test_required_strategy_rejects_different_strategy() -> None:
    context = make_context(
        constraints={
            "required_strategy": "map_reduce",
        }
    )

    with pytest.raises(
        ValueError,
        match="does not satisfy required_strategy",
    ):
        make_handoff(
            make_planner(
                max_tokens=100,
                direct_max_tokens=2_000,
                map_reduce_max_tokens=10_000,
            )
        ).execute(
            text="one two",
            context=context,
            decision=make_decision(context),
        )


def test_allowed_strategies_can_contain_multiple_values() -> None:
    context = make_context(
        constraints={
            "allowed_strategies": [
                "direct",
                "map_reduce",
            ],
        }
    )

    result = make_handoff(
        make_planner(
            max_tokens=100,
            direct_max_tokens=2_000,
        )
    ).execute(
        text="one two",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.strategy in {
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.MAP_REDUCE,
    }


def test_constraints_do_not_modify_v9_planner() -> None:
    planner = make_planner(
        max_tokens=100,
        direct_max_tokens=2_000,
    )

    context = make_context(
        constraints={
            "allowed_strategies": ["direct"],
        }
    )

    result = make_handoff(planner).execute(
        text="one two",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.strategy is SummarizationStrategyType.DIRECT
    assert planner.selector is not None


def test_constraints_preserve_v10_provenance() -> None:
    context = make_context(
        constraints={
            "max_chunks": 2,
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.context_id == context.context_id
    assert result.correlation_id == context.correlation_id


def test_constraints_preserve_v9_source_provenance() -> None:
    text = "The API deployment architecture changed."

    context = make_context()

    result = make_handoff().execute(
        text=text,
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.source_character_count == len(text)
    assert result.plan.source_digest


def test_constraints_do_not_change_intent_handoff() -> None:
    context = make_context(
        intent=SummarizationIntent.TECHNICAL,
        constraints={
            "max_chunks": 2,
        },
    )

    result = make_handoff().execute(
        text="The API deployment architecture changed.",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.intent is SummarizationIntent.TECHNICAL


def test_constraint_handoff_is_deterministic() -> None:
    text = "The API deployment architecture changed."

    context = make_context(
        constraints={
            "max_chunks": 2,
        },
    )

    decision = make_decision(context)

    handoff = make_handoff()

    first = handoff.execute(
        text=text,
        context=context,
        decision=decision,
    )

    second = handoff.execute(
        text=text,
        context=context,
        decision=decision,
    )

    assert first.plan == second.plan
    assert first.context_id == second.context_id
    assert first.correlation_id == second.correlation_id


def test_constraint_handoff_does_not_execute_summarization() -> None:
    context = make_context()

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert not hasattr(result, "summary")
    assert not hasattr(result, "provider")
    assert not hasattr(result, "execution")
