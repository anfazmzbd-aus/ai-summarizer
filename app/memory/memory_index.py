"""
Memory index.
"""

from __future__ import annotations

from .indexed_entry import IndexedEntry


class MemoryIndex:

    def __init__(self) -> None:

        self._entries: list[IndexedEntry] = []

    def add(
        self,
        entry: IndexedEntry,
    ) -> None:

        self._entries.append(entry)

    def all(
        self,
    ) -> list[IndexedEntry]:

        return list(self._entries)

    def count(
        self,
    ) -> int:

        return len(self._entries)
