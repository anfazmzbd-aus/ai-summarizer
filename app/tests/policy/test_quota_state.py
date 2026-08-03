from app.policy import QuotaState


def test_defaults():

    state = QuotaState()

    assert state.queue_depth == 0
    assert state.concurrent_tasks == 0
    assert state.worker_tasks == 0
