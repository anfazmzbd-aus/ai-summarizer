"""
Unified observation model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(slots=True)
class Observation:

    observation_id: UUID = field(default_factory=uuid4)

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    finished_at: datetime | None = None

    def finish(self) -> None:

        self.finished_at = datetime.now(timezone.utc)
