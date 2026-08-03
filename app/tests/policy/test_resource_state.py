from app.policy import ResourceState


def test_defaults():

    state = ResourceState()

    assert state.cpu_percent == 0.0
    assert state.memory_percent == 0.0
    assert state.queue_pressure == 0.0
    assert state.worker_utilization == 0.0
