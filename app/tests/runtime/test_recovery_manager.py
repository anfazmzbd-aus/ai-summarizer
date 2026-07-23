from app.runtime.checkpoint.checkpoint import Checkpoint
from app.runtime.checkpoint.checkpoint_manager import CheckpointManager
from app.runtime.checkpoint.memory_checkpoint_backend import MemoryCheckpointBackend
from app.runtime.checkpoint.recovery_manager import RecoveryManager


def test_recover_latest_state():

    backend = MemoryCheckpointBackend()

    manager = CheckpointManager(
        backend,
    )

    manager.save(
        Checkpoint(
            execution_id="exec-1",
            node="summary",
            state={
                "completed": True,
            },
        )
    )

    recovery = RecoveryManager(
        manager,
    )

    state = recovery.recover(
        "exec-1",
    )

    assert state["completed"] is True


def test_recover_missing_execution():

    backend = MemoryCheckpointBackend()

    manager = CheckpointManager(
        backend,
    )

    recovery = RecoveryManager(
        manager,
    )

    assert recovery.recover("missing") is None
