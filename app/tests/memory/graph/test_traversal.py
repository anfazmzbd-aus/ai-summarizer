from app.memory import (
    GraphEntity,
    GraphRelationship,
    GraphTraversal,
    KnowledgeGraph,
)


def test_neighbors():

    graph = KnowledgeGraph()

    graph.add_entity(
        GraphEntity(
            "A",
            "agent",
        )
    )

    graph.add_entity(
        GraphEntity(
            "B",
            "memory",
        )
    )

    graph.add_relationship(
        GraphRelationship(
            "A",
            "B",
            "USES",
        )
    )

    traversal = GraphTraversal()

    neighbors = traversal.neighbors(
        graph,
        "A",
    )

    assert neighbors == ["B"]
