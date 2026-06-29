# app/orchestration/graph/graph_types.py

from typing import Dict, List, Set, Optional
from pydantic import BaseModel


NodeId = str


class NodeMetadata(BaseModel):
    retryable: bool = True
    timeout_seconds: int = 60
    tags: Set[str] = set()


class NodeContract(BaseModel):
    input_schema: dict
    output_schema: dict
    state_requirements: dict


class GraphNode(BaseModel):
    id: NodeId
    agent: str

    dependencies: List[NodeId] = []

    metadata: NodeMetadata

    contracts: NodeContract


class ExecutionGraph(BaseModel):

    nodes: Dict[NodeId, GraphNode]

    edges: List[tuple[NodeId, NodeId]]

    layers: List[List[NodeId]]