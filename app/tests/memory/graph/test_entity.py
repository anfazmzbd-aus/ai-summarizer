from app.memory import GraphEntity


def test_entity():

    entity = GraphEntity(
        entity_id="customer-1",
        entity_type="customer",
    )

    assert entity.entity_type == "customer"
