"""
Memory indexing service.
"""

from __future__ import annotations

from .indexed_entry import IndexedEntry
from .memory_index import MemoryIndex


class MemoryIndexer:

    def __init__(
        self,
        index: MemoryIndex,
    ) -> None:

        self._index = index

    def index(
        self,
        entry: IndexedEntry,
    ) -> None:

        self._index.add(entry)
