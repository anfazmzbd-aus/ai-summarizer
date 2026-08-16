"""Tests for V9.3-M3 intent integration into deterministic planning."""

from __future__ import annotations

from app.summarization.chunking import ChunkingConfig, TextChunker
from app.summarization.intelligence import SummarizationIntent
from app.summarization.planning import SummarizationPlanner


def make_planner() -> SummarizationPlanner:
    return SummarizationPlanner(
        chunker=TextChunker(
            ChunkingConfig(max_tokens=20, overlap_tokens=0, preserve_boundaries=False)
        )
    )


def test_planner_records_inferred_intent():
    plan = make_planner().plan("The team must follow up with the customer.")
    assert plan.intent is SummarizationIntent.ACTION_ITEMS
    assert plan.intent_classification is not None
    assert plan.metadata["intent"] == "action_items"


def test_planner_accepts_explicit_intent():
    plan = make_planner().plan(
        "The API deployment requires follow up.",
        intent=SummarizationIntent.TECHNICAL,
    )
    assert plan.intent is SummarizationIntent.TECHNICAL
    assert plan.intent_classification is not None
    assert plan.intent_classification.explicit is True


def test_planner_remains_deterministic_with_intent():
    text = "Market trends and recommendations for leadership."
    planner = make_planner()
    assert planner.plan(text) == planner.plan(text)


def test_planner_preserves_existing_strategy_selection():
    plan = make_planner().plan("A neutral document with no intent markers.")
    assert plan.selection.strategy is plan.strategy


def test_planner_default_intent_is_general():
    plan = make_planner().plan("The weather was discussed yesterday.")
    assert plan.intent is SummarizationIntent.GENERAL
