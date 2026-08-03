from app.observability.metrics import Gauge


def test_gauge():

    gauge = Gauge("workers")

    gauge.set(10)

    gauge.increment()

    gauge.decrement(3)

    assert gauge.value == 8
