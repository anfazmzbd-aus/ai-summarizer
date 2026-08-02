import pytest

from app.distributed.adapters import (
    GRPCExecutor,
)

from app.distributed.protocols import (
    TaskEnvelope,
)


class FakeGrpcClient:

    async def execute(
        self,
        payload,
    ):

        return {
            "output": "grpc-result",
            "worker_id": "worker-grpc",
        }


def create_task():

    return TaskEnvelope(
        task_id="task-1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_grpc_success():

    executor = GRPCExecutor(FakeGrpcClient())

    result = await executor.execute(create_task())

    assert result.success

    assert result.output == "grpc-result"

    assert result.worker_id == "worker-grpc"


@pytest.mark.anyio
async def test_grpc_failure():

    class FailedClient:

        async def execute(
            self,
            payload,
        ):

            raise RuntimeError("connection failed")

    executor = GRPCExecutor(FailedClient())

    result = await executor.execute(create_task())

    assert result.success is False

    assert "connection failed" in result.error
