from app.memory.vector import VectorDocument


def test_document():

    document = VectorDocument(
        document_id="1",
        content="summary",
        embedding=[0.1, 0.2],
    )

    assert document.content == "summary"
