"""
Tests for the V9.3-M1 deterministic intelligent summarization planner.
"""

from __future__ import annotations

import hashlib

import pytest

from app.summarization.chunking import ChunkingConfig, TextChunker
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


def test_planner_builds_plan_from_existing_v92_components():
    planner = make_planner(max_tokens=3)

    plan = planner.plan("one two three four five")

    assert isinstance(plan, SummarizationPlan)
    assert plan.chunk_count == 2
    assert plan.token_count == 5
    assert plan.strategy is SummarizationStrategyType.DIRECT
    assert [chunk.index for chunk in plan.chunks] == [0, 1]


def test_planner_delegates_strategy_selection():
    planner = make_planner(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=5,
    )

    plan = planner.plan("one two three four")

    assert plan.strategy is SummarizationStrategyType.MAP_REDUCE
    assert plan.selection.strategy is SummarizationStrategyType.MAP_REDUCE


def test_planner_selects_hierarchical_using_existing_selector():
    planner = make_planner(
        max_tokens=2,
        direct_max_tokens=2,
        map_reduce_max_tokens=3,
    )

    plan = planner.plan("one two three four")

    assert plan.strategy is SummarizationStrategyType.HIERARCHICAL


def test_planner_handles_empty_document():
    plan = make_planner().plan("")

    assert plan.chunks == ()
    assert plan.chunk_count == 0
    assert plan.token_count == 0
    assert plan.strategy is SummarizationStrategyType.DIRECT
    assert plan.source_character_count == 0


def test_planner_preserves_chunk_provenance():
    plan = make_planner(max_tokens=2).plan("one two three four")

    assert tuple(chunk.index for chunk in plan.chunks) == (0, 1)
    assert plan.metadata["chunk_indexes"] == (0, 1)
    assert plan.chunks[0].start_offset == 0
    assert plan.chunks[0].text == "one two"


def test_planner_preserves_existing_chunk_metrics():
    plan = make_planner(max_tokens=2).plan("one two three")

    assert plan.token_count == sum(chunk.token_count for chunk in plan.chunks)
    assert plan.chunk_count == len(plan.chunks)


def test_planner_source_character_count_matches_input():
    text = "Hello, deterministic planner."

    plan = make_planner().plan(text)

    assert plan.source_character_count == len(text)


def test_planner_source_digest_is_deterministic():
    text = "deterministic source"

    plan = make_planner().plan(text)

    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()

    assert plan.source_digest == expected


def test_planner_is_deterministic():
    planner = make_planner(max_tokens=3)
    text = "one two three four five six"

    first = planner.plan(text)
    second = planner.plan(text)

    assert first == second


def test_planner_uses_configured_chunker():
    chunker = TextChunker(
        ChunkingConfig(
            max_tokens=2,
            overlap_tokens=0,
            preserve_boundaries=False,
        )
    )
    planner = SummarizationPlanner(chunker=chunker)

    plan = planner.plan("one two three four")

    assert [chunk.text for chunk in plan.chunks] == [
        "one two",
        "three four",
    ]


def test_planner_uses_configured_selector():
    selector = SummarizationStrategySelector(
        StrategySelectionConfig(
            direct_max_tokens=1,
            map_reduce_max_tokens=3,
        )
    )
    planner = SummarizationPlanner(
        chunker=TextChunker(
            ChunkingConfig(
                max_tokens=10,
                preserve_boundaries=False,
            )
        ),
        selector=selector,
    )

    plan = planner.plan("one two")

    assert plan.strategy is SummarizationStrategyType.MAP_REDUCE


def test_planner_has_no_provider_dependency():
    planner = make_planner()

    plan = planner.plan("provider independent")

    assert plan.metadata["planner_version"] == "v9.3-m1"


def test_planner_rejects_non_string_input():
    planner = make_planner()

    with pytest.raises(TypeError, match="text must be a string"):
        planner.plan(123)  # type: ignore[arg-type]


def test_planner_rejects_invalid_chunker():
    with pytest.raises(TypeError, match="chunker must be a TextChunker"):
        SummarizationPlanner(chunker=object())  # type: ignore[arg-type]


def test_plan_is_immutable():
    plan = make_planner().plan("hello")

    with pytest.raises(AttributeError):
        plan.strategy = SummarizationStrategyType.MAP_REDUCE  # type: ignore[misc]


def test_plan_rejects_inconsistent_metrics():
    plan = make_planner().plan("hello")

    with pytest.raises(ValueError, match="chunk_count"):
        SummarizationPlan(
            strategy=plan.strategy,
            selection=plan.selection,
            chunks=plan.chunks,
            token_count=plan.token_count,
            chunk_count=plan.chunk_count + 1,
            source_character_count=plan.source_character_count,
            source_digest=plan.source_digest,
        )
