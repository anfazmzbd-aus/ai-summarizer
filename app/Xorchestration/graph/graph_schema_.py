# app/orchestration/graph/graph_schema_.py

from typing import Iterable

from .graph_types import (
    ExecutionGraph,
    GraphNode,
)


class GraphSchema:

    @staticmethod
    def create(
        nodes: Iterable[GraphNode]
    ) -> ExecutionGraph:

        node_map = {
            node.id: node
            for node in nodes
        }

        edges = []

        for node in node_map.values():

            for dep in node.dependencies:

                edges.append(
                    (dep, node.id)
                )

        return ExecutionGraph(
            nodes=node_map,
            edges=edges,
            layers=[]
        )