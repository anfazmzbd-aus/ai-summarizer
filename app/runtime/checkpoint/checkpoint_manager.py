from .memory_checkpoint_backend import (
    MemoryCheckpointBackend,
)


class CheckpointManager:

    def __init__(
        self,
        backend=None,
    ):

        self._backend = backend or MemoryCheckpointBackend()

    def save(
        self,
        checkpoint,
    ):

        self._backend.save(checkpoint)

    def load(
        self,
        execution_id,
    ):

        return self._backend.load(execution_id)

    def delete(
        self,
        execution_id,
    ):

        self._backend.delete(execution_id)

    def exists(
        self,
        execution_id,
    ):

        return self._backend.exists(execution_id)

    def get(self, execution_id):
        return self._backend.get(execution_id)

    def latest(
        self,
        execution_id,
    ):
        return self._backend.latest(
            execution_id,
        )
