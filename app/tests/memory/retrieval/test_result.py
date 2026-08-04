from app.memory import (
    RetrievalResult,
    VectorDocument,
)


def test_result():

    result = RetrievalResult(
        document=VectorDocument(
            document_id="1",
            content="AI",
            embedding=[1.0],
        ),
        score=0.9,
    )

    assert result.score == 0.9
