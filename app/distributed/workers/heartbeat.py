"""
AI Summarizer V8.0 Distributed Runtime

Worker heartbeat tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class Heartbeat:

    worker_id: str

    timestamp: datetime

    active_tasks: int = 0

    @classmethod
    def create(
        cls,
        worker_id: str,
        active_tasks: int = 0,
    ) -> "Heartbeat":

        return cls(
            worker_id=worker_id,
            timestamp=datetime.now(timezone.utc),
            active_tasks=active_tasks,
        )

    def is_expired(
        self,
        timeout_seconds: int = 30,
    ) -> bool:

        age = (datetime.now(timezone.utc) - self.timestamp).total_seconds()

        return age > timeout_seconds
