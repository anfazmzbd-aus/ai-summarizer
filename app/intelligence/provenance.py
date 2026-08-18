"""
V10 provenance-correlation contract.

Provides one immutable lifecycle identity that correlates intelligence,
planning, runtime, evaluation, and adaptation artifacts without replacing
existing V9 execution or tracing identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ProvenanceContext:
    """Immutable correlation envelope for one V10 orchestration lifecycle.

    ``correlation_id`` is the stable root identity. Existing V9 identifiers,
    including runtime ``execution_id`` and distributed ``trace_id``, remain
    owned by their existing subsystems and are referenced here when available.
    """

    correlation_id: UUID = field(default_factory=uuid4)
    context_id: UUID | None = None

    task_decision_id: UUID | None = None
    plan_id: UUID | None = None
    execution_id: UUID | None = None

    evaluation_id: UUID | None = None
    adaptation_id: UUID | None = None

    parent_correlation_id: UUID | None = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        compare=False,
    )

    def __post_init__(self) -> None:
        for name in (
            "correlation_id",
            "context_id",
            "task_decision_id",
            "plan_id",
            "execution_id",
            "evaluation_id",
            "adaptation_id",
            "parent_correlation_id",
        ):
            value = getattr(self, name)
            if value is not None and not isinstance(value, UUID):
                raise TypeError(f"{name} must be a UUID or None")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

    @classmethod
    def create(
        cls,
        *,
        context_id: UUID | None = None,
        task_decision_id: UUID | None = None,
        plan_id: UUID | None = None,
        execution_id: UUID | None = None,
        evaluation_id: UUID | None = None,
        adaptation_id: UUID | None = None,
        parent_correlation_id: UUID | None = None,
    ) -> "ProvenanceContext":
        """Create a new lifecycle correlation context."""
        return cls(
            context_id=context_id,
            task_decision_id=task_decision_id,
            plan_id=plan_id,
            execution_id=execution_id,
            evaluation_id=evaluation_id,
            adaptation_id=adaptation_id,
            parent_correlation_id=parent_correlation_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return {
            "adaptation_id": (
                str(self.adaptation_id) if self.adaptation_id is not None else None
            ),
            "context_id": (
                str(self.context_id) if self.context_id is not None else None
            ),
            "correlation_id": str(self.correlation_id),
            "created_at": self.created_at.isoformat(),
            "evaluation_id": (
                str(self.evaluation_id) if self.evaluation_id is not None else None
            ),
            "execution_id": (
                str(self.execution_id) if self.execution_id is not None else None
            ),
            "parent_correlation_id": (
                str(self.parent_correlation_id)
                if self.parent_correlation_id is not None
                else None
            ),
            "plan_id": (str(self.plan_id) if self.plan_id is not None else None),
            "task_decision_id": (
                str(self.task_decision_id)
                if self.task_decision_id is not None
                else None
            ),
        }

    def to_json(self) -> str:
        """Return a canonical JSON representation."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )


__all__ = ["ProvenanceContext"]
