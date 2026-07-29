from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class TimelineEvent:
    """
    Single execution timeline event.
    """

    timestamp: datetime

    event: str

    details: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionTimeline:
    """
    Ordered runtime event log.
    """

    events: list[TimelineEvent] = field(default_factory=list)

    def record(
        self,
        event: str,
        **details,
    ) -> None:
        self.events.append(
            TimelineEvent(
                timestamp=datetime.now(UTC),
                event=event,
                details=details,
            )
        )
