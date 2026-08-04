from app.memory import GraphRelationship


def test_relationship():

    relationship = GraphRelationship(
        source="customer",
        target="order",
        relation="PLACED",
    )

    assert relationship.relation == "PLACED"
