from app.runtime.checkpoint.checkpoint import Checkpoint
from app.runtime.checkpoint.checkpoint_manager import CheckpointManager
from app.runtime.checkpoint.memory_checkpoint_backend import MemoryCheckpointBackend


def test_manager_save():

    backend = MemoryCheckpointBackend()

    manager = CheckpointManager(
        backend,
    )

    checkpoint = Checkpoint(
        execution_id="1",
        node="summary",
        state={},
    )

    manager.save(checkpoint)

    assert manager.latest("1") == checkpoint


def test_manager_latest():

    backend = MemoryCheckpointBackend()

    manager = CheckpointManager(
        backend,
    )

    manager.save(
        Checkpoint(
            execution_id="1",
            node="summary",
            state={},
        )
    )

    manager.save(
        Checkpoint(
            execution_id="1",
            node="risk",
            state={},
        )
    )

    assert manager.latest("1").node == "risk"
