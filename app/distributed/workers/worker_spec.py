"""
AI Summarizer V8.0 Distributed Runtime

Worker specification model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class WorkerStatus(str, Enum):
    """
    Worker lifecycle state.
    """

    STARTING = "starting"

    READY = "ready"

    BUSY = "busy"

    DEGRADED = "degraded"

    OFFLINE = "offline"


@dataclass(slots=True)
class WorkerSpec:
    """
    Distributed worker identity and capabilities.
    """

    worker_id: str

    hostname: str

    capabilities: list[str] = field(default_factory=list)

    max_concurrency: int = 1

    status: WorkerStatus = WorkerStatus.STARTING

    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    active_tasks: int = 0

    def heartbeat(self) -> None:
        """
        Update worker heartbeat timestamp.
        """

        self.last_heartbeat = datetime.now(timezone.utc)
