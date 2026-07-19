from app.runtime.parallel_executor import ParallelExecutor


def square(value: int) -> int:
    return value * value


def test_parallel_executor_returns_results() -> None:
    executor = ParallelExecutor(max_workers=2)

    results = executor.execute(
        square,
        [1, 2, 3, 4],
    )

    assert results == [1, 4, 9, 16]


def test_parallel_executor_preserves_order() -> None:
    executor = ParallelExecutor(max_workers=4)

    results = executor.execute(
        lambda x: x,
        [5, 1, 9, 3],
    )

    assert results == [5, 1, 9, 3]
