from app.distributed.adapters import (
    AdapterFactory,
    GRPCExecutor,
    HTTPExecutor,
    LocalExecutor,
)


class FakeEngine:
    pass


class FakeClient:
    pass


def test_local_adapter():

    adapter = AdapterFactory.create(
        "local",
        execution_engine=FakeEngine(),
    )

    assert isinstance(
        adapter,
        LocalExecutor,
    )


def test_http_adapter():

    adapter = AdapterFactory.create(
        "http",
        endpoint="http://localhost",
    )

    assert isinstance(
        adapter,
        HTTPExecutor,
    )


def test_grpc_adapter():

    adapter = AdapterFactory.create(
        "grpc",
        client=FakeClient(),
    )

    assert isinstance(
        adapter,
        GRPCExecutor,
    )
