import pytest
import httpx

from app.distributed.adapters import (
    HTTPExecutor,
)

from app.distributed.protocols import (
    TaskEnvelope,
)


class MockTransport(httpx.AsyncBaseTransport):

    async def handle_async_request(
        self,
        request,
    ):

        return httpx.Response(
            status_code=200,
            json={
                "output": "remote-result",
                "worker_id": "worker-remote-1",
            },
        )


def create_task():

    return TaskEnvelope(
        task_id="task-1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_http_executor_success():

    client = httpx.AsyncClient(transport=MockTransport())

    executor = HTTPExecutor(
        endpoint="http://runtime/tasks",
        client=client,
    )

    result = await executor.execute(create_task())

    await client.aclose()

    assert result.success

    assert result.output == "remote-result"

    assert result.worker_id == "worker-remote-1"


@pytest.mark.anyio
async def test_http_executor_failure():

    class FailedTransport(httpx.AsyncBaseTransport):

        async def handle_async_request(
            self,
            request,
        ):

            return httpx.Response(status_code=500)

    client = httpx.AsyncClient(transport=FailedTransport())

    executor = HTTPExecutor(
        endpoint="http://runtime/tasks",
        client=client,
    )

    result = await executor.execute(create_task())

    await client.aclose()

    assert result.success is False

    assert result.error is not None
