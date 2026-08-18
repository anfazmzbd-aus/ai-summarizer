"""
V10 task-decision contract.

Defines the provider-independent, declarative decision made by the
intelligence layer before domain-specific planning or runtime execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


class TaskAction(str, Enum):
    """Supported V10 orchestration task actions."""

    SUMMARIZE = "summarize"
    RETRIEVE = "retrieve"
    VERIFY = "verify"
    REFINE = "refine"
    RETRY = "retry"
    FALLBACK = "fallback"
    ABORT = "abort"


@dataclass(frozen=True, slots=True)
class TaskDecision:
    """Immutable, provider-independent declaration of the next task.

    The decision describes what the orchestration layer has decided to do.
    It does not execute the task, select a provider, or own runtime objects.
    """

    action: TaskAction
    context_id: UUID
    correlation_id: UUID
    reason: str = ""
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        compare=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.action, TaskAction):
            raise TypeError("action must be a TaskAction")

        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")

        if not isinstance(self.confidence, (int, float)) or isinstance(
            self.confidence, bool
        ):
            raise TypeError("confidence must be a number")

        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @classmethod
    def create(
        cls,
        *,
        action: TaskAction,
        context_id: UUID,
        correlation_id: UUID,
        reason: str = "",
        confidence: float = 1.0,
        metadata: Mapping[str, Any] | None = None,
    ) -> "TaskDecision":
        """Create a task decision while preserving supplied provenance IDs."""
        return cls(
            action=action,
            context_id=context_id,
            correlation_id=correlation_id,
            reason=reason,
            confidence=confidence,
            metadata={} if metadata is None else metadata,
        )


__all__ = ["TaskAction", "TaskDecision"]
