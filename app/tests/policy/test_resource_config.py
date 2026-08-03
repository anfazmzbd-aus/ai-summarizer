from app.policy import ResourceConfig


def test_defaults():

    config = ResourceConfig()

    assert config.max_cpu_percent == 90.0
    assert config.max_memory_percent == 90.0
    assert config.max_queue_pressure == 0.90
    assert config.max_worker_utilization == 0.95
