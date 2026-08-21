"""
V10 decision effectiveness contracts.

Defines the immutable, provider-independent representation used to describe
how effective an intelligence decision proved to be after execution.

This module contains contracts only. It does not evaluate decisions, mutate
runtime state, perform adaptive actions, or invoke external providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID


class EffectivenessStatus(str, Enum):
    """Supported decision-effectiveness states."""

    EFFECTIVE = "effective"
    DEGRADED = "degraded"
    INEFFECTIVE = "ineffective"
    UNKNOWN = "unknown"


class EffectivenessDimension(str, Enum):
    """Supported effectiveness dimensions."""

    OUTCOME = "outcome"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"


@dataclass(frozen=True, slots=True)
class DecisionEffectiveness:
    """
    Immutable result describing the effectiveness of one intelligence decision.

    The contract contains interpretation only. It does not prescribe retry,
    replanning, provider switching, strategy changes, or any other runtime
    action.
    """

    context_id: UUID
    correlation_id: UUID
    execution_id: str

    status: EffectivenessStatus

    dimensions: Mapping[
        EffectivenessDimension,
        EffectivenessStatus,
    ] = field(default_factory=dict)

    reasons: tuple[str, ...] = ()

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(self.correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string")

        if not self.execution_id:
            raise ValueError("execution_id must not be empty")

        if not isinstance(self.status, EffectivenessStatus):
            raise TypeError("status must be an EffectivenessStatus")

        if not isinstance(self.dimensions, Mapping):
            raise TypeError("dimensions must be a mapping")

        normalized_dimensions: dict[
            EffectivenessDimension,
            EffectivenessStatus,
        ] = {}

        for dimension, status in self.dimensions.items():
            if not isinstance(dimension, EffectivenessDimension):
                raise TypeError("dimension keys must be EffectivenessDimension values")

            if not isinstance(status, EffectivenessStatus):
                raise TypeError("dimension values must be EffectivenessStatus values")

            normalized_dimensions[dimension] = status

        if not isinstance(self.reasons, tuple):
            raise TypeError("reasons must be a tuple")

        for reason in self.reasons:
            if not isinstance(reason, str):
                raise TypeError("reasons must contain strings")

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
        context_id: UUID,
        correlation_id: UUID,
        execution_id: str,
        status: EffectivenessStatus,
        dimensions: (
            Mapping[
                EffectivenessDimension,
                EffectivenessStatus,
            ]
            | None
        ) = None,
        reasons: tuple[str, ...] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> "DecisionEffectiveness":
        """Create an immutable decision-effectiveness result."""

        return cls(
            context_id=context_id,
            correlation_id=correlation_id,
            execution_id=execution_id,
            status=status,
            dimensions={} if dimensions is None else dimensions,
            reasons=reasons,
            metadata={} if metadata is None else metadata,
        )


__all__ = [
    "DecisionEffectiveness",
    "EffectivenessDimension",
    "EffectivenessStatus",
]
