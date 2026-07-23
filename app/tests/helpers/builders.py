from app.orchestration.execution.node_execution_result import (
    NodeExecutionResult,
)
from app.orchestration.graph.graph_schema import ExecutionLayer


def make_layer(*nodes, index=0):
    return ExecutionLayer(
        index=index,
        nodes=tuple(nodes),
    )


def make_result(node, **output):
    return NodeExecutionResult(
        node=node,
        output=output,
    )
