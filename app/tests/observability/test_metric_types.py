from app.observability.metrics import MetricType


def test_metric_types():

    assert MetricType.COUNTER.value == "counter"
    assert MetricType.GAUGE.value == "gauge"
    assert MetricType.HISTOGRAM.value == "histogram"
