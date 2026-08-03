"""
Span lifecycle representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(slots=True)
class Span:

    name: str

    trace_id: UUID

    span_id: UUID = field(default_factory=uuid4)

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    ended_at: datetime | None = None

    def end(
        self,
    ) -> None:

        self.ended_at = datetime.now(timezone.utc)

    @property
    def duration_ms(
        self,
    ) -> float | None:

        if self.ended_at is None:
            return None

        return (self.ended_at - self.started_at).total_seconds() * 1000
