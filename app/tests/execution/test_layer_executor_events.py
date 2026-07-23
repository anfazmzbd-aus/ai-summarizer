from unittest.mock import Mock

from app.orchestration.execution.layer_executor import LayerExecutor
from app.orchestration.execution.node_execution_result import (
    NodeExecutionResult,
)
from app.orchestration.graph.graph_schema import ExecutionLayer


def test_layer_executor_emits_events():

    node_executor = Mock()

    node_executor.execute.return_value = NodeExecutionResult(
        node="summary",
        output={
            "summary": "hello",
        },
    )

    publisher = Mock()

    executor = LayerExecutor(
        node_executor=node_executor,
        events=publisher,
    )

    state = Mock()
    state.node_outputs = {}
    state.artifacts = {}

    layer = ExecutionLayer(
        index=0,
        nodes=("summary",),
    )

    executor.execute_layer(
        layer,
        state,
    )

    publisher.layer_started.assert_called_once_with(0)
    publisher.layer_finished.assert_called_once_with(0)

    assert state.node_outputs == {"summary": {"summary": "hello"}}

    assert state.artifacts == {"summary": "hello"}
