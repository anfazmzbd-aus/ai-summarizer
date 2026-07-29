from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ExecutionMetrics:
    """
    Aggregated runtime execution metrics.

    Metrics are collected during execution and
    exported after completion.
    """

    total_layers: int = 0

    completed_layers: int = 0

    total_nodes: int = 0

    completed_nodes: int = 0

    execution_time_seconds: float = 0.0

    parallel_layers: int = 0

    failed_nodes: int = 0

    retried_nodes: int = 0

    cache_hits: int = 0

    cache_misses: int = 0

    custom: dict[str, object] = field(default_factory=dict)
