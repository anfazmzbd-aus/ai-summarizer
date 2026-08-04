"""
Execution-scoped memory.
"""

from __future__ import annotations

from .memory_entry import MemoryEntry
from .namespace import MemoryNamespace
from .scoped_memory import ScopedMemory


class ExecutionMemory:

    def __init__(
        self,
        memory: ScopedMemory,
        execution_id: str,
    ) -> None:

        self._memory = memory
        self._execution_id = execution_id

    def put(
        self,
        entry: MemoryEntry,
    ) -> None:

        self._memory.put(
            MemoryNamespace.EXECUTION,
            self._execution_id,
            entry,
        )

    def get(
        self,
        key: str,
    ) -> MemoryEntry | None:

        return self._memory.get(
            MemoryNamespace.EXECUTION,
            self._execution_id,
            key,
        )
