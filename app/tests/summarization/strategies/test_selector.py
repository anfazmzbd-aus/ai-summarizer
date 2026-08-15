"""
Tests for deterministic summarization strategy selection.
"""

from __future__ import annotations

import pytest

from app.summarization.strategies.models import (
    StrategySelectionConfig,
    StrategySelectionInput,
    SummarizationStrategyType,
)
from app.summarization.strategies.selector import (
    SummarizationStrategySelector,
)


def test_default_selector_selects_direct_for_small_document():
    result = SummarizationStrategySelector().select(
        StrategySelectionInput(
            token_count=100,
            chunk_count=1,
        )
    )

    assert result.strategy is SummarizationStrategyType.DIRECT


def test_selector_selects_map_reduce_for_medium_document():
    result = SummarizationStrategySelector().select(
        StrategySelectionInput(
            token_count=5_000,
            chunk_count=5,
        )
    )

    assert result.strategy is SummarizationStrategyType.MAP_REDUCE


def test_selector_selects_hierarchical_for_large_document():
    result = SummarizationStrategySelector().select(
        StrategySelectionInput(
            token_count=20_000,
            chunk_count=20,
        )
    )

    assert result.strategy is SummarizationStrategyType.HIERARCHICAL


def test_empty_document_selects_direct():
    result = SummarizationStrategySelector().select(
        StrategySelectionInput(
            token_count=0,
            chunk_count=0,
        )
    )

    assert result.strategy is SummarizationStrategyType.DIRECT


def test_direct_threshold_is_inclusive():
    config = StrategySelectionConfig(
        direct_max_tokens=100,
        map_reduce_max_tokens=500,
    )

    result = SummarizationStrategySelector(config).select(
        StrategySelectionInput(
            token_count=100,
            chunk_count=1,
        )
    )

    assert result.strategy is SummarizationStrategyType.DIRECT


def test_map_reduce_threshold_is_inclusive():
    config = StrategySelectionConfig(
        direct_max_tokens=100,
        map_reduce_max_tokens=500,
    )

    result = SummarizationStrategySelector(config).select(
        StrategySelectionInput(
            token_count=500,
            chunk_count=5,
        )
    )

    assert result.strategy is SummarizationStrategyType.MAP_REDUCE


def test_first_token_above_direct_threshold_selects_map_reduce():
    config = StrategySelectionConfig(
        direct_max_tokens=100,
        map_reduce_max_tokens=500,
    )

    result = SummarizationStrategySelector(config).select(
        StrategySelectionInput(
            token_count=101,
            chunk_count=2,
        )
    )

    assert result.strategy is SummarizationStrategyType.MAP_REDUCE


def test_first_token_above_map_reduce_threshold_selects_hierarchical():
    config = StrategySelectionConfig(
        direct_max_tokens=100,
        map_reduce_max_tokens=500,
    )

    result = SummarizationStrategySelector(config).select(
        StrategySelectionInput(
            token_count=501,
            chunk_count=6,
        )
    )

    assert result.strategy is SummarizationStrategyType.HIERARCHICAL


def test_selector_is_deterministic():
    selector = SummarizationStrategySelector()

    value = StrategySelectionInput(
        token_count=7_500,
        chunk_count=8,
    )

    first = selector.select(value)
    second = selector.select(value)

    assert first == second


def test_selection_preserves_document_metrics():
    value = StrategySelectionInput(
        token_count=4_321,
        chunk_count=7,
    )

    result = SummarizationStrategySelector().select(value)

    assert result.token_count == 4_321
    assert result.chunk_count == 7


def test_selection_contains_reason():
    result = SummarizationStrategySelector().select(
        StrategySelectionInput(
            token_count=100,
            chunk_count=1,
        )
    )

    assert result.reason


def test_selection_contains_threshold_metadata():
    result = SummarizationStrategySelector().select(
        StrategySelectionInput(
            token_count=100,
            chunk_count=1,
        )
    )

    assert result.metadata["direct_max_tokens"] == 2_000

    assert result.metadata["map_reduce_max_tokens"] == 10_000


def test_config_rejects_zero_direct_threshold():
    with pytest.raises(
        ValueError,
        match="direct_max_tokens",
    ):
        StrategySelectionConfig(
            direct_max_tokens=0,
        )


def test_config_rejects_zero_map_reduce_threshold():
    with pytest.raises(
        ValueError,
        match="map_reduce_max_tokens",
    ):
        StrategySelectionConfig(
            map_reduce_max_tokens=0,
        )


def test_config_rejects_invalid_threshold_order():
    with pytest.raises(
        ValueError,
        match="map_reduce_max_tokens",
    ):
        StrategySelectionConfig(
            direct_max_tokens=1_000,
            map_reduce_max_tokens=500,
        )


def test_selection_input_rejects_negative_tokens():
    with pytest.raises(
        ValueError,
        match="token_count",
    ):
        StrategySelectionInput(
            token_count=-1,
            chunk_count=1,
        )


def test_selection_input_rejects_negative_chunks():
    with pytest.raises(
        ValueError,
        match="chunk_count",
    ):
        StrategySelectionInput(
            token_count=10,
            chunk_count=-1,
        )
