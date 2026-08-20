"""
V10 execution observation contract.

Defines the provider-independent, immutable representation of what happened
during one execution.

The observation is a historical fact. It does not own runtime components,
providers, clients, executors, callbacks, or exception objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


class ExecutionOutcome(str, Enum):
    """Normalized outcomes produced by an execution."""

    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class ExecutionObservation:
    """Immutable provider-independent observation of one execution.

    The observation describes what actually happened during execution.
    It deliberately does not contain runtime implementation objects or
    planning state.

    RuntimeDecision describes intended execution behavior.
    ExecutionObservation describes the resulting execution facts.
    """

    execution_id: str
    context_id: UUID
    correlation_id: UUID

    outcome: ExecutionOutcome

    duration_ms: float = 0.0

    retry_count: int = 0
    fallback_used: bool = False

    error_type: str | None = None
    error_message: str | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string")

        if not self.execution_id:
            raise ValueError("execution_id must not be empty")

        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.outcome, ExecutionOutcome):
            raise TypeError("outcome must be an ExecutionOutcome")

        if not isinstance(self.duration_ms, (int, float)) or isinstance(
            self.duration_ms, bool
        ):
            raise TypeError("duration_ms must be a number")

        if self.duration_ms < 0:
            raise ValueError("duration_ms must be greater than or equal to 0")

        if not isinstance(self.retry_count, int) or isinstance(self.retry_count, bool):
            raise TypeError("retry_count must be an integer")

        if self.retry_count < 0:
            raise ValueError("retry_count must be greater than or equal to 0")

        if not isinstance(self.fallback_used, bool):
            raise TypeError("fallback_used must be a bool")

        if self.error_type is not None and not isinstance(self.error_type, str):
            raise TypeError("error_type must be a string or None")

        if self.error_message is not None and not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string or None")

        if self.outcome is ExecutionOutcome.FAILED:
            if not self.error_type:
                raise ValueError("error_type must be provided when outcome is FAILED")

            if not self.error_message:
                raise ValueError(
                    "error_message must be provided when outcome is FAILED"
                )

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @classmethod
    def create(
        cls,
        *,
        execution_id: str,
        context_id: UUID,
        correlation_id: UUID,
        outcome: ExecutionOutcome,
        duration_ms: float = 0.0,
        retry_count: int = 0,
        fallback_used: bool = False,
        error_type: str | None = None,
        error_message: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "ExecutionObservation":
        """Create an execution observation while preserving provenance IDs."""

        return cls(
            execution_id=execution_id,
            context_id=context_id,
            correlation_id=correlation_id,
            outcome=outcome,
            duration_ms=duration_ms,
            retry_count=retry_count,
            fallback_used=fallback_used,
            error_type=error_type,
            error_message=error_message,
            metadata={} if metadata is None else metadata,
        )


__all__ = ["ExecutionObservation", "ExecutionOutcome"]
