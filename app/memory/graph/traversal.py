"""
Graph traversal helpers.
"""

from __future__ import annotations

from .graph import KnowledgeGraph
from .relationship import GraphRelationship


class GraphTraversal:

    def neighbors(
        self,
        graph: KnowledgeGraph,
        entity_id: str,
    ) -> list[str]:

        return [
            relationship.target
            for relationship in graph.relationships
            if relationship.source == entity_id
        ]

    def outgoing(
        self,
        graph: KnowledgeGraph,
        entity_id: str,
    ) -> list[GraphRelationship]:

        return [
            relationship
            for relationship in graph.relationships
            if relationship.source == entity_id
        ]
