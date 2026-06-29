from dataclasses import dataclass
from dataclasses import field

from typing import Optional
from typing import Any

from app.orchestration.graph.graph_schema import (
    NodeStatus,
)


# --------------------------
# Runtime State
# --------------------------

@dataclass
class RuntimeNodeState:

    status: NodeStatus = (
        "pending"
    )

    retries: int = 0

    duration_ms: float = 0

    started_at: Optional[
        str
    ] = None

    ended_at: Optional[
        str
    ] = None

    error: Optional[
        str
    ] = None


# --------------------------
# Layer Trace
# --------------------------

@dataclass
class LayerTrace:

    index: int

    nodes: tuple[
        str,
        ...
    ]

    duration_ms: float = 0


# --------------------------
# Execution Context
# --------------------------

@dataclass
class ExecutionContext:

    execution_id: str = ""

    runtime: dict[
        str,
        RuntimeNodeState
    ] = field(
        default_factory=dict
    )

    completed_layers: list[
        int
    ] = field(
        default_factory=list
    )

    traces: list[
        LayerTrace
    ] = field(
        default_factory=list
    )

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    # ------------------

    def begin_node(
        self,
        node_name,
    ):

        state = (
            self.runtime
            .get(
                node_name
            )
        )

        if state is None:

            state = (
                RuntimeNodeState()
            )

            self.runtime[
                node_name
            ] = state

        state.status = (
            "running"
        )

    # ------------------

    def success(
        self,
        node_name,
        duration_ms,
    ):

        node = (
            self.runtime[
                node_name
            ]
        )

        node.status = (
            "success"
        )

        node.duration_ms = (
            duration_ms
        )

    # ------------------

    def fail(
        self,
        node_name,
        error,
    ):

        node = (
            self.runtime[
                node_name
            ]
        )

        node.status = (
            "failed"
        )

        node.error = str(
            error
        )

    # ------------------

    def retry(
        self,
        node_name,
    ):

        node = (
            self.runtime[
                node_name
            ]
        )

        node.status = (
            "retry"
        )

        node.retries += 1

    # ------------------

    def complete_layer(
        self,
        index,
        duration_ms,
        nodes,
    ):

        self.completed_layers.append(
            index
        )

        self.traces.append(

            LayerTrace(

                index=index,

                duration_ms=(
                    duration_ms
                ),

                nodes=tuple(
                    nodes
                )

            )

        )