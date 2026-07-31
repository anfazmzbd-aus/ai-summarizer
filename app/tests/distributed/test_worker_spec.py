from app.distributed.workers import (
    WorkerSpec,
    WorkerStatus,
)


def test_worker_creation():

    worker = WorkerSpec(
        worker_id="worker-001",
        hostname="localhost",
        capabilities=[
            "summary",
            "analysis",
        ],
    )

    assert worker.worker_id == "worker-001"

    assert worker.status == WorkerStatus.STARTING


def test_worker_heartbeat():

    worker = WorkerSpec(
        worker_id="worker-001",
        hostname="localhost",
    )

    previous = worker.last_heartbeat

    worker.heartbeat()

    assert worker.last_heartbeat >= previous
