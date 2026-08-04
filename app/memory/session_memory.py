"""
Session-scoped memory.
"""

from __future__ import annotations

from .memory_entry import MemoryEntry
from .namespace import MemoryNamespace
from .scoped_memory import ScopedMemory


class SessionMemory:

    def __init__(
        self,
        memory: ScopedMemory,
        session_id: str,
    ) -> None:

        self._memory = memory
        self._session_id = session_id

    def put(
        self,
        entry: MemoryEntry,
    ) -> None:

        self._memory.put(
            MemoryNamespace.SESSION,
            self._session_id,
            entry,
        )

    def get(
        self,
        key: str,
    ) -> MemoryEntry | None:

        return self._memory.get(
            MemoryNamespace.SESSION,
            self._session_id,
            key,
        )
