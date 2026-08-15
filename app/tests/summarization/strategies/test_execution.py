"""
Tests for provider-independent strategy execution.
"""

from __future__ import annotations

import pytest

from app.summarization.chunking.models import Chunk
from app.summarization.strategies.execution import (
    StrategyExecutor,
)
from app.summarization.strategies.models import (
    SummarizationStrategyType,
)


def make_chunk(
    index: int,
    text: str,
) -> Chunk:
    return Chunk(
        index=index,
        text=text,
        token_count=len(text.split()),
        character_count=len(text),
        start_offset=index * 10,
        end_offset=(index * 10) + len(text),
    )


def summarize(text: str) -> str:
    return f"[{text}]"


def test_executor_registers_all_default_strategies():
    executor = StrategyExecutor()

    assert executor.registered_strategies() == (
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.MAP_REDUCE,
        SummarizationStrategyType.HIERARCHICAL,
    )


def test_executor_dispatches_direct():
    executor = StrategyExecutor()

    result = executor.execute(
        SummarizationStrategyType.DIRECT,
        [make_chunk(0, "hello")],
        summarize,
    )

    assert result.strategy is SummarizationStrategyType.DIRECT


def test_executor_dispatches_map_reduce():
    executor = StrategyExecutor()

    result = executor.execute(
        SummarizationStrategyType.MAP_REDUCE,
        [
            make_chunk(0, "hello"),
            make_chunk(1, "world"),
        ],
        summarize,
    )

    assert result.strategy is SummarizationStrategyType.MAP_REDUCE


def test_executor_dispatches_hierarchical():
    executor = StrategyExecutor()

    result = executor.execute(
        SummarizationStrategyType.HIERARCHICAL,
        [
            make_chunk(0, "one"),
            make_chunk(1, "two"),
            make_chunk(2, "three"),
        ],
        summarize,
    )

    assert result.strategy is SummarizationStrategyType.HIERARCHICAL


def test_executor_rejects_unknown_strategy():
    executor = StrategyExecutor()

    with pytest.raises(
        ValueError,
        match="unsupported strategy",
    ):
        executor.execute(
            "unknown",  # type: ignore[arg-type]
            [],
            summarize,
        )


def test_executor_requires_callable():
    executor = StrategyExecutor()

    with pytest.raises(
        TypeError,
        match="callable",
    ):
        executor.execute(
            SummarizationStrategyType.DIRECT,
            [],
            None,  # type: ignore[arg-type]
        )


def test_executor_preserves_source_order():
    calls: list[str] = []

    def recording_summarize(text: str) -> str:
        calls.append(text)
        return text.upper()

    executor = StrategyExecutor()

    executor.execute(
        SummarizationStrategyType.MAP_REDUCE,
        [
            make_chunk(0, "first"),
            make_chunk(1, "second"),
            make_chunk(2, "third"),
        ],
        recording_summarize,
    )

    assert calls[:3] == [
        "first",
        "second",
        "third",
    ]


def test_executor_is_deterministic():
    chunks = [
        make_chunk(0, "one"),
        make_chunk(1, "two"),
    ]

    executor = StrategyExecutor()

    first = executor.execute(
        SummarizationStrategyType.DIRECT,
        chunks,
        summarize,
    )

    second = executor.execute(
        SummarizationStrategyType.DIRECT,
        chunks,
        summarize,
    )

    assert first == second
