"""
Complete V9.3-M4 adaptive strategy planning tests.
"""

from __future__ import annotations

import pytest

# from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.intelligence import (
    DocumentProfiler,
    # DocumentStructureType,
    SummarizationIntent,
)
from app.summarization.planning.adaptive import AdaptiveStrategyPlanner
from app.summarization.strategies.models import (
    StrategySelection,
    SummarizationStrategyType,
)


def selection(strategy, *, token_count=10, chunk_count=2):
    return StrategySelection(
        strategy=strategy,
        token_count=token_count,
        chunk_count=chunk_count,
        reason="baseline",
        metadata={},
    )


def profile(text: str):
    return DocumentProfiler().profile(text)


def test_direct_prose_without_signal_is_retained():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT),
        profile("Plain prose without special structure."),
        SummarizationIntent.GENERAL,
    )
    assert decision.selected_strategy is SummarizationStrategyType.DIRECT
    assert decision.promoted is False


@pytest.mark.parametrize(
    ("intent", "signal"),
    [
        (SummarizationIntent.ACTION_ITEMS, "intent:action_items"),
        (SummarizationIntent.FINDINGS, "intent:findings"),
        (SummarizationIntent.INSIGHTS, "intent:insights"),
        (SummarizationIntent.TECHNICAL, "intent:technical"),
    ],
)
def test_direct_strategy_is_promoted_for_intent(intent, signal):
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT),
        profile("Plain prose with enough content."),
        intent,
    )
    assert decision.selected_strategy is SummarizationStrategyType.MAP_REDUCE
    assert decision.promoted is True
    assert signal in decision.signals


@pytest.mark.parametrize(
    "text",
    [
        "# Heading\n\nFirst section.\n\nSecond section.",
        "- item one\n- item two\n\nMore content.",
        "```python\nprint('x')\n```\n\nMore content.",
    ],
)
def test_direct_strategy_is_promoted_for_structured_documents(text):
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT),
        profile(text),
        SummarizationIntent.GENERAL,
    )
    assert decision.selected_strategy is SummarizationStrategyType.MAP_REDUCE
    assert decision.promoted is True


def test_single_chunk_direct_strategy_is_retained():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT, chunk_count=1),
        profile("# Heading\n\nStructured content."),
        SummarizationIntent.TECHNICAL,
    )
    assert decision.selected_strategy is SummarizationStrategyType.DIRECT
    assert decision.promoted is False
    assert "single_chunk" in decision.signals


def test_map_reduce_is_never_downgraded():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.MAP_REDUCE),
        profile("Plain prose."),
        SummarizationIntent.GENERAL,
    )
    assert decision.selected_strategy is SummarizationStrategyType.MAP_REDUCE
    assert decision.promoted is False


def test_hierarchical_is_never_downgraded():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.HIERARCHICAL, token_count=20_000),
        profile("Plain prose."),
        SummarizationIntent.GENERAL,
    )
    assert decision.selected_strategy is SummarizationStrategyType.HIERARCHICAL
    assert decision.promoted is False


def test_decision_is_deterministic():
    planner = AdaptiveStrategyPlanner()
    selection_value = selection(SummarizationStrategyType.DIRECT)
    profile_value = profile("# Heading\n\nTechnical implementation details.")
    first = planner.decide(
        selection_value, profile_value, SummarizationIntent.TECHNICAL
    )
    second = planner.decide(
        selection_value, profile_value, SummarizationIntent.TECHNICAL
    )
    assert first == second


def test_decision_is_immutable():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT),
        profile("Plain prose."),
        SummarizationIntent.GENERAL,
    )
    with pytest.raises(AttributeError):
        decision.selected_strategy = SummarizationStrategyType.MAP_REDUCE


def test_rejects_invalid_selection():
    with pytest.raises(TypeError, match="selection"):
        AdaptiveStrategyPlanner().decide(
            object(), profile("text"), SummarizationIntent.GENERAL
        )


def test_rejects_invalid_profile():
    with pytest.raises(TypeError, match="profile"):
        AdaptiveStrategyPlanner().decide(
            selection(SummarizationStrategyType.DIRECT),
            object(),
            SummarizationIntent.GENERAL,
        )


def test_rejects_invalid_intent():
    with pytest.raises(TypeError, match="intent"):
        AdaptiveStrategyPlanner().decide(
            selection(SummarizationStrategyType.DIRECT),
            profile("text"),
            "technical",  # type: ignore[arg-type]
        )


def test_code_structure_signal_is_explicit():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT),
        profile("```python\nprint('hello')\n```\n\nsecond paragraph"),
        SummarizationIntent.GENERAL,
    )
    assert "structure:code" in decision.signals


def test_planner_version_is_recorded():
    decision = AdaptiveStrategyPlanner().decide(
        selection(SummarizationStrategyType.DIRECT),
        profile("text"),
        SummarizationIntent.GENERAL,
    )
    assert decision.metadata["planner_version"] == "v9.3-m4"
