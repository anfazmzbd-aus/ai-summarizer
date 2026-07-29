from dataclasses import dataclass
from datetime import datetime

from .execution_strategy import ExecutionStrategy
from .reasoning_result import ReasoningResult


@dataclass(frozen=True, slots=True)
class Decision:
    strategy: ExecutionStrategy
    reasoning: ReasoningResult
    created_at: datetime
