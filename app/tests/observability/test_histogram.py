from app.observability.metrics import Histogram


def test_histogram():

    metric = Histogram("latency")

    metric.observe(10)

    metric.observe(20)

    metric.observe(30)

    assert metric.count == 3

    assert metric.average == 20
