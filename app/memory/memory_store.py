"""
In-memory implementation.
"""

from __future__ import annotations

from .memory import Memory
from .memory_entry import MemoryEntry


class MemoryStore(Memory):

    def __init__(self) -> None:

        self._entries: dict[str, MemoryEntry] = {}

    def put(
        self,
        entry: MemoryEntry,
    ) -> None:

        self._entries[entry.key] = entry

    def get(
        self,
        key: str,
    ) -> MemoryEntry | None:

        return self._entries.get(key)

    def delete(
        self,
        key: str,
    ) -> None:

        self._entries.pop(key, None)

    def keys(
        self,
    ) -> list[str]:

        return list(self._entries.keys())
