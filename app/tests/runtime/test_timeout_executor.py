from app.runtime.timeout import Timeout
from app.runtime.timeout_executor import TimeoutExecutor


def test_timeout_executor_returns_result():

    executor = TimeoutExecutor(
        Timeout(seconds=5),
    )

    result = executor.run(
        lambda: 123,
    )

    assert result == 123


def test_timeout_executor_passes_arguments():

    executor = TimeoutExecutor(
        Timeout(seconds=5),
    )

    def add(a, b):
        return a + b

    result = executor.run(
        add,
        2,
        3,
    )

    assert result == 5


def test_timeout_executor_preserves_return_type():

    executor = TimeoutExecutor(
        Timeout(seconds=5),
    )

    result = executor.run(
        lambda: {"status": "ok"},
    )

    assert result == {
        "status": "ok",
    }
