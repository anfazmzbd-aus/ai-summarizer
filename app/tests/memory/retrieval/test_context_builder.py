from app.memory import (
    ContextBuilder,
    RetrievalResult,
    VectorDocument,
)


def test_context():

    builder = ContextBuilder()

    context = builder.build(
        [
            RetrievalResult(
                VectorDocument(
                    document_id="1",
                    content="First",
                    embedding=[1],
                ),
                1.0,
            ),
            RetrievalResult(
                VectorDocument(
                    document_id="2",
                    content="Second",
                    embedding=[1],
                ),
                1.0,
            ),
        ]
    )

    assert "First" in context
    assert "Second" in context
