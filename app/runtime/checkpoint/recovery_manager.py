class RecoveryManager:

    def __init__(
        self,
        checkpoint_manager,
    ):
        self._checkpoint_manager = checkpoint_manager

    def recover(
        self,
        execution_id,
    ):
        checkpoint = self._checkpoint_manager.latest(
            execution_id,
        )

        if checkpoint is None:
            return None

        return checkpoint.state

    def can_recover(
        self,
        execution_id,
    ):
        return self._checkpoint_manager.exists(
            execution_id,
        )

    def latest(self, execution_id):
        checkpoint = self._backend.latest(execution_id)

        if checkpoint is None:
            return None

        return checkpoint.state
