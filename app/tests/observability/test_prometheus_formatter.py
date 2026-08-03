from app.observability.metrics import (
    Counter,
    Gauge,
    Histogram,
)

from app.observability.prometheus import (
    PrometheusFormatter,
)


def test_counter_format():

    counter = Counter("runtime.tasks.completed")

    counter.increment(5)

    formatter = PrometheusFormatter()

    result = formatter.format_metric(counter)

    assert "runtime_tasks_completed_total 5" in result


def test_gauge_format():

    gauge = Gauge("runtime.queue.depth")

    gauge.set(3)

    formatter = PrometheusFormatter()

    result = formatter.format_metric(gauge)

    assert "runtime_queue_depth 3" in result


def test_histogram_format():

    histogram = Histogram("runtime.latency")

    histogram.observe(10)

    result = PrometheusFormatter().format_metric(histogram)

    assert "runtime_latency_count 1" in result
