import pytest

from app.distributed.queue import (
    LocalExecutionQueue,
    QueueManager,
)


def test_create_local_queue():

    queue = QueueManager.create("local")

    assert isinstance(
        queue,
        LocalExecutionQueue,
    )


def test_unknown_backend():

    with pytest.raises(ValueError):

        QueueManager.create("unknown")
