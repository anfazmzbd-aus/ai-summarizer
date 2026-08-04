"""
Knowledge graph model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .entity import GraphEntity
from .relationship import GraphRelationship


@dataclass(slots=True)
class KnowledgeGraph:

    entities: dict[str, GraphEntity] = field(default_factory=dict)

    relationships: list[GraphRelationship] = field(default_factory=list)

    def add_entity(
        self,
        entity: GraphEntity,
    ) -> None:

        self.entities[entity.entity_id] = entity

    def add_relationship(
        self,
        relationship: GraphRelationship,
    ) -> None:

        self.relationships.append(relationship)
