# from .checkpoint_backend import CheckpointBackend
from .checkpoint import Checkpoint


class MemoryCheckpointBackend:

    def __init__(self):

        self._checkpoints: dict[str, list[Checkpoint]] = {}

    def save(self, checkpoint):

        self._checkpoints.setdefault(
            checkpoint.execution_id,
            [],
        ).append(checkpoint)

    def list(self, execution_id):

        return self._checkpoints.get(
            execution_id,
            [],
        )

    def latest(
        self,
        execution_id,
    ):

        checkpoints = self.list(execution_id)

        if not checkpoints:
            return None

        return checkpoints[-1]

    def load(
        self,
        execution_id,
    ):

        return self._checkpoints.get(execution_id)

    def delete(self, execution_id):

        self._checkpoints.pop(
            execution_id,
            None,
        )

    def exists(self, execution_id):

        return execution_id in self._checkpoints
