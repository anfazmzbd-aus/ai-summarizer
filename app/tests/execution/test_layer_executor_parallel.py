"""
Tests for LayerExecutor parallel execution behavior.
"""

from unittest.mock import Mock, patch

from app.orchestration.execution.layer_executor import LayerExecutor
from app.orchestration.execution.node_execution_result import (
    NodeExecutionResult,
)
from app.orchestration.graph.graph_schema import ExecutionLayer
from app.runtime.runtime_config import RuntimeConfig


def make_state():
    state = Mock()
    state.node_outputs = {}
    state.artifacts = {}
    return state


def test_layer_executor_sequential_execution():
    node_executor = Mock()

    node_executor.execute.side_effect = [
        NodeExecutionResult(
            node="summary",
            output={"summary": "A"},
        ),
        NodeExecutionResult(
            node="insights",
            output={"insights": "B"},
        ),
    ]

    layer_executor = LayerExecutor(node_executor)

    state = make_state()

    layer = ExecutionLayer(
        index=0,
        nodes=["summary", "insights"],
    )

    layer_executor.execute_layer(
        layer,
        state,
    )

    assert state.node_outputs["summary"]["summary"] == "A"
    assert state.node_outputs["insights"]["insights"] == "B"

    assert state.artifacts["summary"] == "A"
    assert state.artifacts["insights"] == "B"

    assert node_executor.execute.call_count == 2


@patch("app.orchestration.execution.layer_executor.ParallelExecutor")
def test_layer_executor_parallel_execution(
    mock_parallel_executor,
):
    node_executor = Mock()

    parallel_instance = mock_parallel_executor.return_value

    parallel_instance.execute.return_value = [
        NodeExecutionResult(
            node="summary",
            output={"summary": "A"},
        ),
        NodeExecutionResult(
            node="insights",
            output={"insights": "B"},
        ),
    ]

    config = RuntimeConfig(
        parallel_execution=True,
        max_workers=4,
    )

    layer_executor = LayerExecutor(
        node_executor=node_executor,
        runtime_config=config,
    )

    state = make_state()

    layer = ExecutionLayer(
        index=0,
        nodes=["summary", "insights"],
    )

    layer_executor.execute_layer(
        layer,
        state,
    )

    parallel_instance.execute.assert_called_once()

    assert state.node_outputs["summary"]["summary"] == "A"
    assert state.node_outputs["insights"]["insights"] == "B"

    assert state.artifacts["summary"] == "A"
    assert state.artifacts["insights"] == "B"


def test_layer_executor_runtime_config_override():
    node_executor = Mock()

    parallel_executor = Mock()

    parallel_executor.execute.return_value = [
        NodeExecutionResult(
            node="summary",
            output={"summary": "A"},
        ),
        NodeExecutionResult(
            node="insights",
            output={"insights": "B"},
        ),
    ]

    default_config = RuntimeConfig(
        parallel_execution=False,
        max_workers=4,
    )

    override_config = RuntimeConfig(
        parallel_execution=True,
        max_workers=4,
    )

    executor = LayerExecutor(
        node_executor=node_executor,
        runtime_config=default_config,
        parallel_executor=parallel_executor,
    )

    state = make_state()

    layer = ExecutionLayer(
        index=0,
        nodes=["summary", "insights"],
    )

    executor.execute_layer(
        layer,
        state,
        runtime_config=override_config,
    )

    parallel_executor.execute.assert_called_once()


def test_layer_executor_default_config_used_when_no_override():
    node_executor = Mock()

    node_executor.execute.side_effect = [
        NodeExecutionResult(
            node="summary",
            output={"summary": "A"},
        ),
        NodeExecutionResult(
            node="insights",
            output={"insights": "B"},
        ),
    ]

    config = RuntimeConfig(
        parallel_execution=False,
        max_workers=4,
    )

    executor = LayerExecutor(
        node_executor=node_executor,
        runtime_config=config,
    )

    state = make_state()

    layer = ExecutionLayer(
        index=0,
        nodes=["summary", "insights"],
    )

    executor.execute_layer(
        layer,
        state,
    )

    assert node_executor.execute.call_count == 2


def test_layer_executor_override_does_not_mutate_default_config():
    node_executor = Mock()

    parallel_executor = Mock()

    parallel_executor.execute.return_value = []

    default_config = RuntimeConfig(
        parallel_execution=False,
        max_workers=4,
    )

    override = RuntimeConfig(
        parallel_execution=True,
        max_workers=4,
    )

    executor = LayerExecutor(
        node_executor=node_executor,
        runtime_config=default_config,
        parallel_executor=parallel_executor,
    )

    state = make_state()

    layer = ExecutionLayer(
        index=0,
        nodes=["summary", "insights"],
    )

    executor.execute_layer(
        layer,
        state,
        runtime_config=override,
    )

    assert executor._config.parallel_execution is False
