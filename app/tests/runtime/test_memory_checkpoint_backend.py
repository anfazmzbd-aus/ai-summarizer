from app.runtime.checkpoint.checkpoint import Checkpoint
from app.runtime.checkpoint.memory_checkpoint_backend import MemoryCheckpointBackend


def make_checkpoint(node):

    return Checkpoint(
        execution_id="exec-1",
        node=node,
        state={},
    )


def test_save_checkpoint():

    backend = MemoryCheckpointBackend()

    checkpoint = make_checkpoint("summary")

    backend.save(checkpoint)

    assert backend.latest("exec-1") == checkpoint


def test_latest_checkpoint():

    backend = MemoryCheckpointBackend()

    backend.save(make_checkpoint("summary"))
    backend.save(make_checkpoint("insights"))

    latest = backend.latest("exec-1")

    assert latest.node == "insights"


def test_missing_checkpoint():

    backend = MemoryCheckpointBackend()

    assert backend.latest("missing") is None
