"""
Memory search engine.
"""

from __future__ import annotations

from .indexed_entry import IndexedEntry
from .memory_index import MemoryIndex
from .namespace import MemoryNamespace


class MemorySearch:

    def __init__(
        self,
        index: MemoryIndex,
    ) -> None:

        self._index = index

    def search(
        self,
        query: str,
    ) -> list[IndexedEntry]:

        query = query.lower()

        return [
            entry for entry in self._index.all() if query in str(entry.value).lower()
        ]

    def by_namespace(
        self,
        namespace: MemoryNamespace,
    ) -> list[IndexedEntry]:

        return [entry for entry in self._index.all() if entry.namespace is namespace]
