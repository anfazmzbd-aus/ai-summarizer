"""
V10 runtime-decision contract.

Defines the provider-independent, declarative execution constraints selected
by the intelligence layer. The contract does not own or invoke runtime
components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


class ExecutionMode(str, Enum):
    """Execution modes understood by the V10 runtime boundary."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"


@dataclass(frozen=True, slots=True)
class RuntimeDecision:
    """Immutable declaration of how an approved task should be executed.

    This is an orchestration boundary, not a runtime implementation. It does
    not contain runtime objects, providers, clients, executors, or callbacks.
    """

    mode: ExecutionMode
    context_id: UUID
    correlation_id: UUID

    timeout_seconds: float = 60.0

    retry_enabled: bool = False
    max_retry_attempts: int = 0
    retry_delay_seconds: float = 0.0
    retry_exponential_backoff: bool = False

    fallback_allowed: bool = True

    max_workers: int = 1

    metadata: Mapping[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        compare=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.mode, ExecutionMode):
            raise TypeError("mode must be an ExecutionMode")

        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.timeout_seconds, (int, float)) or isinstance(
            self.timeout_seconds, bool
        ):
            raise TypeError("timeout_seconds must be a number")

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

        if not isinstance(self.retry_enabled, bool):
            raise TypeError("retry_enabled must be a bool")

        if not isinstance(self.max_retry_attempts, int) or isinstance(
            self.max_retry_attempts, bool
        ):
            raise TypeError("max_retry_attempts must be an integer")

        if self.max_retry_attempts < 0:
            raise ValueError("max_retry_attempts must be greater than or equal to 0")

        if self.retry_enabled and self.max_retry_attempts < 1:
            raise ValueError(
                "max_retry_attempts must be at least 1 when retry_enabled is True"
            )

        if not self.retry_enabled and self.max_retry_attempts != 0:
            raise ValueError("max_retry_attempts must be 0 when retry_enabled is False")

        if not isinstance(self.retry_delay_seconds, (int, float)) or isinstance(
            self.retry_delay_seconds, bool
        ):
            raise TypeError("retry_delay_seconds must be a number")

        if self.retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be greater than or equal to 0")

        if not isinstance(self.retry_exponential_backoff, bool):
            raise TypeError("retry_exponential_backoff must be a bool")

        if not isinstance(self.fallback_allowed, bool):
            raise TypeError("fallback_allowed must be a bool")

        if not isinstance(self.max_workers, int) or isinstance(self.max_workers, bool):
            raise TypeError("max_workers must be an integer")

        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        if self.mode is ExecutionMode.SEQUENTIAL and self.max_workers != 1:
            raise ValueError("max_workers must be 1 when execution mode is sequential")

        if self.mode is ExecutionMode.PARALLEL and self.max_workers < 2:
            raise ValueError(
                "max_workers must be at least 2 when execution mode is parallel"
            )

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
        mode: ExecutionMode,
        context_id: UUID,
        correlation_id: UUID,
        timeout_seconds: float = 60.0,
        retry_enabled: bool = False,
        max_retry_attempts: int = 0,
        retry_delay_seconds: float = 0.0,
        retry_exponential_backoff: bool = False,
        fallback_allowed: bool = True,
        max_workers: int = 1,
        metadata: Mapping[str, Any] | None = None,
    ) -> "RuntimeDecision":
        """Create a runtime decision while preserving provenance IDs."""
        return cls(
            mode=mode,
            context_id=context_id,
            correlation_id=correlation_id,
            timeout_seconds=timeout_seconds,
            retry_enabled=retry_enabled,
            max_retry_attempts=max_retry_attempts,
            retry_delay_seconds=retry_delay_seconds,
            retry_exponential_backoff=retry_exponential_backoff,
            fallback_allowed=fallback_allowed,
            max_workers=max_workers,
            metadata={} if metadata is None else metadata,
        )


__all__ = ["ExecutionMode", "RuntimeDecision"]
