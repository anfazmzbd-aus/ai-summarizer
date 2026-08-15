"""
Deterministic summarization strategy selector.
"""

from __future__ import annotations

from .models import (
    StrategySelection,
    StrategySelectionConfig,
    StrategySelectionInput,
    SummarizationStrategyType,
)


class SummarizationStrategySelector:
    """
    Select a summarization strategy from deterministic document metrics.
    """

    def __init__(
        self,
        config: StrategySelectionConfig | None = None,
    ) -> None:
        self.config = config or StrategySelectionConfig()

    def select(
        self,
        selection_input: StrategySelectionInput,
    ) -> StrategySelection:
        if selection_input.chunk_count == 0:
            strategy = SummarizationStrategyType.DIRECT
            reason = "empty document"

        elif selection_input.token_count <= self.config.direct_max_tokens:
            strategy = SummarizationStrategyType.DIRECT
            reason = "document is within direct threshold"

        elif selection_input.token_count <= self.config.map_reduce_max_tokens:
            strategy = SummarizationStrategyType.MAP_REDUCE
            reason = "document is within map-reduce threshold"

        else:
            strategy = SummarizationStrategyType.HIERARCHICAL
            reason = "document exceeds map-reduce threshold"

        return StrategySelection(
            strategy=strategy,
            token_count=selection_input.token_count,
            chunk_count=selection_input.chunk_count,
            reason=reason,
            metadata={
                "direct_max_tokens": (self.config.direct_max_tokens),
                "map_reduce_max_tokens": (self.config.map_reduce_max_tokens),
            },
        )
