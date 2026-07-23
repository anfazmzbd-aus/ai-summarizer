from unittest.mock import Mock

from app.runtime.middleware_pipeline import MiddlewarePipeline


def test_before_execution_order():

    pipeline = MiddlewarePipeline()

    first = Mock()
    second = Mock()

    order = []

    first.before_execution.side_effect = lambda context: order.append("first")

    second.before_execution.side_effect = lambda context: order.append("second")

    pipeline.add(first)
    pipeline.add(second)

    pipeline.before_execution(
        Mock(),
    )

    assert order == [
        "first",
        "second",
    ]


def test_after_execution_reverse_order():

    pipeline = MiddlewarePipeline()

    first = Mock()
    second = Mock()

    order = []

    first.after_execution.side_effect = lambda context, result: order.append("first")

    second.after_execution.side_effect = lambda context, result: order.append("second")

    pipeline.add(first)
    pipeline.add(second)

    pipeline.after_execution(
        Mock(),
        {},
    )

    assert order == [
        "second",
        "first",
    ]


def test_pipeline_with_no_middlewares():

    pipeline = MiddlewarePipeline()

    pipeline.before_execution(
        Mock(),
    )

    pipeline.after_execution(
        Mock(),
        {},
    )
