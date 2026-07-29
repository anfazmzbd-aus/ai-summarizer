from dataclasses import dataclass, field
from datetime import datetime, timezone

from .execution_strategy import ExecutionStrategy
from .reasoning_result import ReasoningResult


@dataclass(frozen=True, slots=True)
class Decision:
    strategy: ExecutionStrategy
    reasoning: ReasoningResult
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        compare=False,
    )
