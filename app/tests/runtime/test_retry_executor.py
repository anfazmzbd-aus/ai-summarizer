from app.runtime.retry_executor import RetryExecutor
from app.runtime.retry_policy import RetryPolicy


def test_success_first_attempt() -> None:
    executor = RetryExecutor(RetryPolicy())

    result = executor.run(lambda: 123)

    assert result == 123


def test_retry_then_success() -> None:
    counter = {"count": 0}

    def func():
        counter["count"] += 1

        if counter["count"] < 2:
            raise RuntimeError()

        return "ok"

    executor = RetryExecutor(RetryPolicy())

    assert executor.run(func) == "ok"
    assert counter["count"] == 2


def test_retry_failure() -> None:
    executor = RetryExecutor(RetryPolicy(max_attempts=2))

    calls = {"count": 0}

    def func():
        calls["count"] += 1
        raise RuntimeError()

    import pytest

    with pytest.raises(RuntimeError):
        executor.run(func)

    assert calls["count"] == 2
