from __future__ import annotations

from app.runtime.persistence.persistence_backend import PersistenceBackend


class MemoryBackend(PersistenceBackend):
    """
    In-memory persistence backend.

    Used for:
    - testing
    - local runtime persistence
    - development environments
    """

    def __init__(self):

        self._records = {}

    def load(
        self,
        execution_id: str,
    ):

        return self.get(
            execution_id,
        )

    def save(
        self,
        record,
    ) -> None:

        self._records[record.execution_id] = record

    def get(
        self,
        execution_id: str,
    ):

        return self._records.get(
            execution_id,
        )

    def delete(
        self,
        execution_id: str,
    ) -> None:

        self._records.pop(
            execution_id,
            None,
        )

    def list(
        self,
    ) -> list:

        return list(self._records.values())

    def exists(
        self,
        execution_id: str,
    ) -> bool:

        return execution_id in self._records
