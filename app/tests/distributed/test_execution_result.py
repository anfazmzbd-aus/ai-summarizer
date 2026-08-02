from app.distributed.adapters import (
    RemoteExecutionResult,
)


def test_execution_result():

    result = RemoteExecutionResult(
        success=True,
        output="ok",
    )

    assert result.success

    assert result.output == "ok"
