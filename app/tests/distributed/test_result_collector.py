from app.distributed.coordinator import (
    ExecutionResult,
    ResultCollector,
)


def test_add_result():

    collector = ResultCollector()

    result = ExecutionResult(
        task_id="task-001",
        success=True,
        output="done",
    )

    collector.add(result)

    assert collector.count() == 1


def test_get_result():

    collector = ResultCollector()

    result = ExecutionResult(
        task_id="task-001",
        success=True,
    )

    collector.add(result)

    assert collector.get("task-001") == result
