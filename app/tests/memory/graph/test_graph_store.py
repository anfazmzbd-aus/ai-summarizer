from app.memory import GraphStore


def test_graph_store():

    store = GraphStore()

    assert store.graph is not None
