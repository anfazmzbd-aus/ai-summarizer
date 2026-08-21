"""
V10 experience repository boundary.

Defines a storage-neutral repository contract for normalized decision
experiences.

The boundary does not prescribe SQLite, Redis, vector storage, files,
external databases, embeddings, or any other persistence technology.
"""

from __future__ import annotations

from typing import Protocol, TypeAlias, runtime_checkable
from uuid import UUID

from .experience_normalization import (
    ExperienceComparisonKey,
    NormalizedDecisionExperience,
)


ExperienceProvenanceKey: TypeAlias = tuple[
    UUID,
    UUID,
    str,
]


@runtime_checkable
class ExperienceRepository(Protocol):
    """
    Storage-neutral repository boundary for normalized experiences.

    Implementations are append-only at this architectural stage.
    """

    def add(
        self,
        experience: NormalizedDecisionExperience,
    ) -> None:
        """Add one normalized experience."""

    def get(
        self,
        *,
        context_id: UUID,
        correlation_id: UUID,
        execution_id: str,
    ) -> NormalizedDecisionExperience | None:
        """Return one experience by exact provenance."""

    def find_by_comparison_key(
        self,
        comparison_key: ExperienceComparisonKey,
    ) -> tuple[NormalizedDecisionExperience, ...]:
        """Return experiences with an exact semantic comparison key."""

    def list_all(
        self,
    ) -> tuple[NormalizedDecisionExperience, ...]:
        """Return all experiences in deterministic repository order."""


def experience_provenance_key(
    experience: NormalizedDecisionExperience,
) -> ExperienceProvenanceKey:
    """Return the stable provenance identity for one experience."""

    if not isinstance(
        experience,
        NormalizedDecisionExperience,
    ):
        raise TypeError("experience must be a NormalizedDecisionExperience")

    return (
        experience.context_id,
        experience.correlation_id,
        experience.execution_id,
    )


__all__ = [
    "ExperienceProvenanceKey",
    "ExperienceRepository",
    "experience_provenance_key",
]
