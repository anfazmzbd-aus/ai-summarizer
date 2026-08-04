"""
Scoped memory implementation.
"""

from __future__ import annotations

from .memory_entry import MemoryEntry
from .memory_store import MemoryStore
from .namespace import MemoryNamespace


class ScopedMemory:

    def __init__(self) -> None:

        self._stores: dict[
            tuple[MemoryNamespace, str],
            MemoryStore,
        ] = {}

    def store(
        self,
        namespace: MemoryNamespace,
        scope: str,
    ) -> MemoryStore:

        key = (namespace, scope)

        if key not in self._stores:
            self._stores[key] = MemoryStore()

        return self._stores[key]

    def put(
        self,
        namespace: MemoryNamespace,
        scope: str,
        entry: MemoryEntry,
    ) -> None:

        self.store(namespace, scope).put(entry)

    def get(
        self,
        namespace: MemoryNamespace,
        scope: str,
        key: str,
    ) -> MemoryEntry | None:

        return self.store(namespace, scope).get(key)
