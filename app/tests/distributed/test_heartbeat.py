from app.distributed.workers import Heartbeat


def test_create_heartbeat():

    heartbeat = Heartbeat.create("worker-001")

    assert heartbeat.worker_id == "worker-001"

    assert heartbeat.active_tasks == 0


def test_heartbeat_not_expired():

    heartbeat = Heartbeat.create("worker-001")

    assert not heartbeat.is_expired()
