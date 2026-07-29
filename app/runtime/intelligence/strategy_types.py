from enum import Enum


class ExecutionStrategyType(str, Enum):
    DEFAULT = "default"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    RECOVERY = "recovery"
