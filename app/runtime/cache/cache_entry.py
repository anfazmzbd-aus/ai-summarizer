from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CacheEntry:

    key: str

    value: object

    created_at: datetime
