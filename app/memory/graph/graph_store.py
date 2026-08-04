"""
In-memory graph store.
"""

from __future__ import annotations

from .graph import KnowledgeGraph


class GraphStore:

    def __init__(self) -> None:

        self._graph = KnowledgeGraph()

    @property
    def graph(
        self,
    ) -> KnowledgeGraph:

        return self._graph
