from __future__ import annotations

from dataclasses import dataclass

from app.runtime.observability.execution_metrics import ExecutionMetrics
from app.runtime.observability.execution_timeline import ExecutionTimeline
from app.runtime.observability.strategy_snapshot import StrategySnapshot


@dataclass(slots=True)
class RuntimeSnapshot:
    """
    Captures execution observability data.
    """

    metrics: ExecutionMetrics

    timeline: ExecutionTimeline

    strategy: StrategySnapshot | None = None
