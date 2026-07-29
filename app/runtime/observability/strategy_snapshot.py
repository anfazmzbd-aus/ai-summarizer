from __future__ import annotations

from dataclasses import dataclass

from app.runtime.intelligence.execution_strategy import ExecutionStrategy


@dataclass(slots=True)
class StrategySnapshot:
    """
    Immutable snapshot of the strategy used
    during one execution.
    """

    strategy: ExecutionStrategy
