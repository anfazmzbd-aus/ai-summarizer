from app.memory import (
    GraphEntity,
    GraphRelationship,
    KnowledgeGraph,
)


def test_graph():

    graph = KnowledgeGraph()

    graph.add_entity(
        GraphEntity(
            "1",
            "customer",
        )
    )

    graph.add_relationship(
        GraphRelationship(
            "1",
            "2",
            "OWNS",
        )
    )

    assert len(graph.entities) == 1
    assert len(graph.relationships) == 1
