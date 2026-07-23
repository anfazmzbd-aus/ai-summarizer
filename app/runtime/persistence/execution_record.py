from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ExecutionRecord:
    """
    Persistent representation of a runtime execution.
    """

    execution_id: str

    status: str

    started_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    completed_at: datetime | None = None

    outputs: dict = field(
        default_factory=dict,
    )

    metadata: dict = field(
        default_factory=dict,
    )
