from __future__ import annotations


class PersistenceManager:
    """
    Runtime persistence coordinator.

    Delegates storage operations to the configured backend.
    """

    def __init__(
        self,
        backend,
    ):

        self._backend = backend

    def save(
        self,
        record,
    ) -> None:

        self._backend.save(
            record,
        )

    def get(
        self,
        execution_id: str,
    ):

        return self._backend.get(
            execution_id,
        )

    def delete(
        self,
        execution_id: str,
    ) -> None:

        self._backend.delete(
            execution_id,
        )

    def list(
        self,
    ) -> list:

        return self._backend.list()

    def exists(
        self,
        execution_id: str,
    ) -> bool:

        return self._backend.exists(
            execution_id,
        )
