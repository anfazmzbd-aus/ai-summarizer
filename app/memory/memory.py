"""
Memory interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .memory_entry import MemoryEntry


class Memory(ABC):

    @abstractmethod
    def put(
        self,
        entry: MemoryEntry,
    ) -> None: ...

    @abstractmethod
    def get(
        self,
        key: str,
    ) -> MemoryEntry | None: ...

    @abstractmethod
    def delete(
        self,
        key: str,
    ) -> None: ...

    @abstractmethod
    def keys(
        self,
    ) -> list[str]: ...
