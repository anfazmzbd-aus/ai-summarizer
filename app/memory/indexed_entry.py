"""
Indexed memory entry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .namespace import MemoryNamespace


@dataclass(slots=True)
class IndexedEntry:

    key: str

    namespace: MemoryNamespace

    scope: str

    value: Any

    metadata: dict[str, Any] = field(default_factory=dict)
