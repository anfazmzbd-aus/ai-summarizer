"""
AI Summarizer V8.0 Distributed Runtime

Task message contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class TaskEnvelope:
    """
    Distributed execution task message.

    Represents a unit of work dispatched to a worker.
    """

    task_id: str

    execution_id: str

    node_id: str

    agent_type: str

    payload: dict[str, Any] = field(default_factory=dict)

    priority: int = 0

    retry_count: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    metadata: dict[str, Any] = field(default_factory=dict)

    def increment_retry(self) -> None:
        """
        Increase retry attempt counter.
        """

        self.retry_count += 1
