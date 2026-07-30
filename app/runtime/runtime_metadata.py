"""
AI Summarizer V7.8 Runtime Metadata

Defines immutable metadata associated with a single runtime execution.
This object tracks the execution lifecycle and timing information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from app.runtime.observability.runtime_snapshot import RuntimeSnapshot
from app.runtime.diagnostics.runtime_diagnostics import (
    RuntimeDiagnostics,
)
from app.runtime.reporting.runtime_report import RuntimeReport


class RuntimeStatus(str, Enum):
    """Lifecycle states for a runtime execution."""

    NEW = "NEW"
    INITIALIZING = "INITIALIZING"
    VALIDATING = "VALIDATING"
    SCHEDULING = "SCHEDULING"
    EXECUTING = "EXECUTING"
    FINALIZING = "FINALIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class RuntimeMetadata:
    """
    Runtime execution metadata.

    This object contains operational metadata describing the execution.
    It intentionally excludes business state and execution results.
    """

    execution_id: UUID = field(default_factory=uuid4)

    status: RuntimeStatus = RuntimeStatus.NEW

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    started_at: datetime | None = None

    completed_at: datetime | None = None

    runtime_version: str = "7.8.0"

    graph_version: str = "7.7"

    scheduler_version: str = "7.7"

    observability: RuntimeSnapshot | None = None

    diagnostics: RuntimeDiagnostics | None = None

    report: RuntimeReport | None = None

    @property
    def duration_seconds(self) -> float | None:
        """
        Returns the execution duration in seconds.

        Returns None if execution has not completed.
        """

        if self.started_at is None or self.completed_at is None:
            return None

        return (self.completed_at - self.started_at).total_seconds()
