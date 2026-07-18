"""
AI Summarizer V7.8 Runtime Context

Defines the top-level runtime container for a single execution.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.orchestration.execution.execution_context import ExecutionContext

from .cancellation_token import CancellationToken
from .runtime_config import RuntimeConfig
from .runtime_metadata import RuntimeMetadata
from datetime import datetime, timezone

from .runtime_metadata import RuntimeStatus


@dataclass(slots=True)
class RuntimeContext:
    """
    Top-level runtime context.

    Owns every runtime-scoped object associated with a single execution.
    """

    execution_context: ExecutionContext

    config: RuntimeConfig

    metadata: RuntimeMetadata

    cancellation_token: CancellationToken

    def mark_initializing(self) -> None:
        self.metadata.status = RuntimeStatus.INITIALIZING

    def mark_scheduling(self) -> None:
        self.metadata.status = RuntimeStatus.SCHEDULING

    def mark_executing(self) -> None:
        self.metadata.status = RuntimeStatus.EXECUTING
        self.metadata.started_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        self.metadata.status = RuntimeStatus.COMPLETED
        self.metadata.completed_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        self.metadata.status = RuntimeStatus.FAILED
        self.metadata.completed_at = datetime.now(timezone.utc)
