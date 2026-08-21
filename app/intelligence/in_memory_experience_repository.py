"""
V10 in-memory experience repository.

Provides a deterministic reference implementation of ExperienceRepository.

This implementation exists to validate the repository boundary and support
offline tests. It is not a production persistence decision.
"""

from __future__ import annotations

from uuid import UUID

from .experience_normalization import (
    ExperienceComparisonKey,
    NormalizedDecisionExperience,
)
from .experience_repository import (
    ExperienceProvenanceKey,
    experience_provenance_key,
)


class InMemoryExperienceRepository:
    """
    Deterministic append-only in-memory experience repository.

    Experiences are indexed independently by:
    - provenance identity
    - semantic comparison key

    Existing entries are never overwritten.
    """

    def __init__(self) -> None:
        self._by_provenance: dict[
            ExperienceProvenanceKey,
            NormalizedDecisionExperience,
        ] = {}

        self._by_comparison_key: dict[
            ExperienceComparisonKey,
            list[NormalizedDecisionExperience],
        ] = {}

        self._ordered: list[NormalizedDecisionExperience] = []

    def add(
        self,
        experience: NormalizedDecisionExperience,
    ) -> None:
        """Add one normalized experience without overwriting existing data."""

        if not isinstance(
            experience,
            NormalizedDecisionExperience,
        ):
            raise TypeError("experience must be a NormalizedDecisionExperience")

        provenance_key = experience_provenance_key(experience)

        if provenance_key in self._by_provenance:
            raise ValueError("experience provenance already exists")

        self._by_provenance[provenance_key] = experience

        matches = self._by_comparison_key.setdefault(
            experience.comparison_key,
            [],
        )
        matches.append(experience)

        self._ordered.append(experience)

    def get(
        self,
        *,
        context_id: UUID,
        correlation_id: UUID,
        execution_id: str,
    ) -> NormalizedDecisionExperience | None:
        """Return one experience by exact provenance."""

        self._validate_provenance(
            context_id=context_id,
            correlation_id=correlation_id,
            execution_id=execution_id,
        )

        return self._by_provenance.get(
            (
                context_id,
                correlation_id,
                execution_id,
            )
        )

    def find_by_comparison_key(
        self,
        comparison_key: ExperienceComparisonKey,
    ) -> tuple[NormalizedDecisionExperience, ...]:
        """
        Return exact semantic matches in deterministic insertion order.

        This method deliberately performs no similarity calculation.
        """

        if not isinstance(comparison_key, tuple):
            raise TypeError("comparison_key must be a tuple")

        matches = self._by_comparison_key.get(
            comparison_key,
            [],
        )

        return tuple(matches)

    def list_all(
        self,
    ) -> tuple[NormalizedDecisionExperience, ...]:
        """Return all experiences in deterministic insertion order."""

        return tuple(self._ordered)

    @staticmethod
    def _validate_provenance(
        *,
        context_id: UUID,
        correlation_id: UUID,
        execution_id: str,
    ) -> None:
        if not isinstance(context_id, UUID):
            raise TypeError("context_id must be a UUID")

        if not isinstance(correlation_id, UUID):
            raise TypeError("correlation_id must be a UUID")

        if not isinstance(execution_id, str):
            raise TypeError("execution_id must be a string")

        if not execution_id:
            raise ValueError("execution_id must not be empty")


__all__ = ["InMemoryExperienceRepository"]
