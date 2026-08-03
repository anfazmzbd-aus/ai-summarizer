from app.policy import QuotaConfig


def test_defaults():

    config = QuotaConfig()

    assert config.max_queue_depth == 1000
    assert config.max_concurrent_tasks == 100
    assert config.max_worker_tasks == 10
