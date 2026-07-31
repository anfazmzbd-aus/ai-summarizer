from app.distributed.workers import WorkerRegistry
from app.distributed.workers.worker_spec import (
    WorkerSpec,
    WorkerStatus,
)


def create_worker():

    return WorkerSpec(
        worker_id="worker-001",
        hostname="localhost",
        status=WorkerStatus.READY,
    )


def test_register_worker():

    registry = WorkerRegistry()

    worker = create_worker()

    registry.register(worker)

    assert registry.count() == 1


def test_get_worker():

    registry = WorkerRegistry()

    worker = create_worker()

    registry.register(worker)

    result = registry.get("worker-001")

    assert result == worker


def test_ready_workers():

    registry = WorkerRegistry()

    registry.register(create_worker())

    assert len(registry.ready_workers()) == 1


def test_remove_worker():

    registry = WorkerRegistry()

    registry.register(create_worker())

    registry.remove("worker-001")

    assert registry.count() == 0
