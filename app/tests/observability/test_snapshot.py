from app.observability.metrics import (
    # Counter,
    MetricSnapshot,
)


def test_snapshot():

    snapshot = MetricSnapshot(
        name="tasks",
        metric_type="counter",
        value=10,
    )

    assert snapshot.name == "tasks"

    assert snapshot.value == 10
