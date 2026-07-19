from app.orchestration.execution.node_execution_result import (
    NodeExecutionResult,
)


def test_node_execution_result():
    result = NodeExecutionResult(
        node="summary",
        output={"summary": "hello"},
    )

    assert result.node == "summary"
    assert result.output["summary"] == "hello"
