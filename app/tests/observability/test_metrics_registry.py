from app.observability.metrics import (
    Counter,
    MetricsRegistry,
)


def test_register():

    registry = MetricsRegistry()

    registry.register(Counter("tasks"))

    assert registry.contains("tasks")


def test_duplicate():

    registry = MetricsRegistry()

    registry.register(Counter("tasks"))

    try:

        registry.register(Counter("tasks"))

        assert False

    except ValueError:

        assert True


def test_snapshot():

    registry = MetricsRegistry()

    counter = registry.register(Counter("tasks"))

    counter.increment(5)

    snapshots = registry.snapshot()

    assert len(snapshots) == 1

    assert snapshots[0].value == 5
