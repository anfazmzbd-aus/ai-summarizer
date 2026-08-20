"""
V10 deterministic execution evaluation result contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


class EvaluationStatus(str, Enum):
    """Overall assessment of an execution."""

    PASS = "pass"
    FAIL = "fail"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Immutable evaluation result for one execution."""

    execution_id: str
    context_id: UUID
    correlation_id: UUID

    status: EvaluationStatus

    dimensions: Mapping[str, EvaluationStatus] = field(default_factory=dict)

    reasons: tuple[str, ...] = ()

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

        if not isinstance(self.status, EvaluationStatus):
            raise TypeError("status must be an EvaluationStatus")

        if not isinstance(self.dimensions, Mapping):
            raise TypeError("dimensions must be a mapping")

        normalized_dimensions: dict[str, EvaluationStatus] = {}

        for name, value in self.dimensions.items():
            if not isinstance(name, str):
                raise TypeError("dimension names must be strings")

            if not name:
                raise ValueError("dimension names must not be empty")

            if not isinstance(value, EvaluationStatus):
                raise TypeError("dimension values must be EvaluationStatus values")

            normalized_dimensions[name] = value

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("evaluation reasons must be strings")

        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(
            self,
            "dimensions",
            MappingProxyType(normalized_dimensions),
        )

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
        status: EvaluationStatus,
        dimensions: Mapping[str, EvaluationStatus] | None = None,
        reasons: tuple[str, ...] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> "EvaluationResult":
        """Create an immutable evaluation result."""

        return cls(
            execution_id=execution_id,
            context_id=context_id,
            correlation_id=correlation_id,
            status=status,
            dimensions={} if dimensions is None else dimensions,
            reasons=reasons,
            metadata={} if metadata is None else metadata,
        )


__all__ = ["EvaluationResult", "EvaluationStatus"]
