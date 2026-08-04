from app.memory.vector import (
    VectorDocument,
    VectorStore,
)


def test_store():

    store = VectorStore()

    store.add(
        VectorDocument(
            document_id="1",
            content="AI summary",
            embedding=[1, 0],
        )
    )

    assert store.count() == 1

    assert store.get("1") is not None


def test_search():

    store = VectorStore()

    store.add(
        VectorDocument(
            document_id="1",
            content="AI",
            embedding=[1, 0],
        )
    )

    result = store.search([1, 0])

    assert result[0].document_id == "1"
