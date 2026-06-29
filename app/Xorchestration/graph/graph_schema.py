from dataclasses import dataclass, field
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Any
from typing import Literal


ExecutionStage = Literal[
    "preprocessing",
    "dag"
]

NodeStatus = Literal[
    "pending",
    "running",
    "success",
    "failed",
    "skipped",
    "retry"
]


# --------------------------------
# Node Contract
# --------------------------------

@dataclass(frozen=True)
class GraphNode:

    name: str

    stage: ExecutionStage

    function_name: str

    depends_on: List[str] = field(
        default_factory=list
    )

    reads: Set[str] = field(
        default_factory=set
    )

    writes: Set[str] = field(
        default_factory=set
    )

    retryable: bool = True

    timeout_seconds: float = 30.0

    max_retries: int = 1

    metadata: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )


# --------------------------------
# Edge Contract
# --------------------------------

@dataclass(frozen=True)
class GraphEdge:

    source: str

    target: str


# --------------------------------
# Layer Contract
# --------------------------------

@dataclass(frozen=True)
class ExecutionLayer:

    index: int

    nodes: List[str]


# --------------------------------
# Runtime Node State
# --------------------------------

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


# --------------------------------
# Execution Graph
# --------------------------------

@dataclass
class ExecutionGraph:

    execution_id: str

    nodes: Dict[
        str,
        GraphNode
    ]

    edges: List[
        GraphEdge
    ]

    layers: List[
        ExecutionLayer
    ]

    selected_agents: List[
        str
    ]

    root_nodes: List[
        str
    ]

    leaf_nodes: List[
        str
    ]

    runtime: Dict[
        str,
        RuntimeNodeState
    ] = field(
        default_factory=dict
    )

    metadata: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    version: str = (
        "7.7"
    )