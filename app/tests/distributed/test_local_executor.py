import pytest

from app.distributed.adapters import (
    LocalExecutor,
)

from app.distributed.protocols import (
    TaskEnvelope,
)


class FakeExecutionEngine:

    async def execute(
        self,
        task,
    ):

        return {"summary": "done"}


@pytest.mark.anyio
async def test_local_executor():

    executor = LocalExecutor(FakeExecutionEngine())

    task = TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )

    result = await executor.execute(task)

    assert result.success

    assert result.output["summary"] == "done"
