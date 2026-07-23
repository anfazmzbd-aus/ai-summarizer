from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Checkpoint:
    """
    Runtime execution checkpoint.

    Represents a recoverable execution state
    after a node completes.
    """

    execution_id: str

    node: str

    state: dict

    created_at: datetime = field(
        default_factory=datetime.utcnow,
    )
