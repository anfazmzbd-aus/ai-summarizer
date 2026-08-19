"""
Complete tests for the V10 strategy policy handoff.
"""

from __future__ import annotations

import pytest

from app.intelligence import (
    ConstraintAwarePlannerHandoff,
    IntelligenceContext,
    PlannerHandoff,
    StrategyPolicyHandoff,
    StrategyPolicyResult,
    TaskAction,
    TaskDecision,
)
from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.planning import SummarizationPlanner
from app.summarization.strategies.models import (
    StrategySelectionConfig,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import SummarizationStrategySelector


def make_planner(
    *,
    max_tokens: int = 100,
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
) -> IntelligenceContext:
    return IntelligenceContext.create(
        request_id="m2-4-test",
        constraints=constraints or {},
    )


def make_decision(
    context: IntelligenceContext,
) -> TaskDecision:
    return TaskDecision.create(
        action=TaskAction.SUMMARIZE,
        context_id=context.context_id,
        correlation_id=context.correlation_id,
        reason="strategy policy test",
        confidence=1.0,
    )


def make_handoff(
    planner: SummarizationPlanner | None = None,
) -> StrategyPolicyHandoff:
    planner = planner or make_planner()

    return StrategyPolicyHandoff(ConstraintAwarePlannerHandoff(PlannerHandoff(planner)))


def test_returns_strategy_policy_result() -> None:
    context = make_context()

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert isinstance(result, StrategyPolicyResult)


def test_result_preserves_selected_strategy() -> None:
    context = make_context()

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.selected_strategy is SummarizationStrategyType.DIRECT
    assert result.plan.strategy is result.selected_strategy


def test_preference_is_satisfied_when_selected_strategy_matches() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "direct",
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.preference_satisfied is True
    assert result.preference_overridden is False


def test_preference_is_not_enforced() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "map_reduce",
        }
    )

    result = make_handoff(
        make_planner(
            max_tokens=100,
            direct_max_tokens=2_000,
            map_reduce_max_tokens=10_000,
        )
    ).execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.selected_strategy is SummarizationStrategyType.DIRECT
    assert result.preference_satisfied is False
    assert result.preference_overridden is True


def test_preference_does_not_override_v93_selection() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "hierarchical",
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.selected_strategy is SummarizationStrategyType.DIRECT
    assert result.preference_satisfied is False


def test_no_preference_returns_none() -> None:
    context = make_context()

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.preference_satisfied is None
    assert result.preference_overridden is False


def test_allowed_strategy_is_enforced() -> None:
    context = make_context(
        constraints={
            "allowed_strategies": ["map_reduce"],
        }
    )

    with pytest.raises(
        ValueError,
        match="selected strategy 'direct' is not allowed",
    ):
        make_handoff().execute(
            text="one two three",
            context=context,
            decision=make_decision(context),
        )


def test_required_strategy_is_enforced() -> None:
    context = make_context(
        constraints={
            "required_strategy": "map_reduce",
        }
    )

    with pytest.raises(
        ValueError,
        match="does not satisfy required_strategy",
    ):
        make_handoff().execute(
            text="one two three",
            context=context,
            decision=make_decision(context),
        )


def test_required_strategy_succeeds_when_v93_selects_it() -> None:
    context = make_context(
        constraints={
            "required_strategy": "map_reduce",
        }
    )

    result = make_handoff(
        make_planner(
            max_tokens=100,
            direct_max_tokens=2,
            map_reduce_max_tokens=10_000,
        )
    ).execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.selected_strategy is SummarizationStrategyType.MAP_REDUCE


def test_preference_and_allowed_strategy_can_coexist() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "map_reduce",
            "allowed_strategies": [
                "direct",
                "map_reduce",
            ],
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.selected_strategy is SummarizationStrategyType.DIRECT
    assert result.preference_satisfied is False


def test_preference_and_required_strategy_can_coexist() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "map_reduce",
            "required_strategy": "map_reduce",
        }
    )

    result = make_handoff(
        make_planner(
            max_tokens=100,
            direct_max_tokens=2,
            map_reduce_max_tokens=10_000,
        )
    ).execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.selected_strategy is SummarizationStrategyType.MAP_REDUCE
    assert result.preference_satisfied is True


def test_preference_does_not_modify_plan() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "map_reduce",
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.strategy is SummarizationStrategyType.DIRECT
    assert result.plan.strategy is result.selected_strategy


def test_result_preserves_v10_provenance() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "direct",
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.context_id == context.context_id
    assert result.correlation_id == context.correlation_id


def test_result_preserves_v9_source_provenance() -> None:
    text = "The API deployment architecture changed."
    context = make_context()

    result = make_handoff().execute(
        text=text,
        context=context,
        decision=make_decision(context),
    )

    assert result.plan.source_character_count == len(text)
    assert result.plan.source_digest


def test_strategy_policy_does_not_invoke_provider() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "direct",
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert not hasattr(result, "provider")
    assert not hasattr(result, "client")
    assert not hasattr(result, "summary")


def test_strategy_policy_is_deterministic() -> None:
    text = "one two three"

    context = make_context(
        constraints={
            "preferred_strategy": "direct",
        }
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

    assert first.selected_strategy is second.selected_strategy
    assert first.preference_satisfied == second.preference_satisfied
    assert first.plan == second.plan


def test_policy_result_exposes_underlying_handoff() -> None:
    context = make_context(
        constraints={
            "preferred_strategy": "direct",
        }
    )

    result = make_handoff().execute(
        text="one two three",
        context=context,
        decision=make_decision(context),
    )

    assert result.handoff.plan is result.plan
    assert result.handoff.context_id == result.context_id
    assert result.handoff.correlation_id == result.correlation_id
