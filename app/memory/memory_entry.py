"""
Memory entry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class MemoryEntry:

    key: str

    value: Any

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    metadata: dict[str, Any] = field(default_factory=dict)
