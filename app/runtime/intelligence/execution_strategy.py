from dataclasses import dataclass

from .strategy_types import ExecutionStrategyType


@dataclass(frozen=True, slots=True)
class ExecutionStrategy:
    strategy: ExecutionStrategyType
    parallel_execution: bool
    use_cache: bool
    enable_retry: bool
    checkpoint_enabled: bool
    timeout_multiplier: float
