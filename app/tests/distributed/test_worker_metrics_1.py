from app.distributed.workers import WorkerMetrics


def test_metrics_receive():

    metrics = WorkerMetrics()

    metrics.record_received()

    assert metrics.tasks_received == 1


def test_metrics_completion():

    metrics = WorkerMetrics()

    metrics.start_task()

    metrics.record_completed(2.5)

    assert metrics.tasks_completed == 1

    assert metrics.active_tasks == 0

    assert metrics.total_execution_time == 2.5


def test_metrics_failure():

    metrics = WorkerMetrics()

    metrics.start_task()

    metrics.record_failed()

    assert metrics.tasks_failed == 1
