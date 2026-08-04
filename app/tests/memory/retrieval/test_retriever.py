from app.memory import (
    RetrievalQuery,
    Retriever,
    VectorDocument,
    VectorStore,
)
from app.memory.vector import EmbeddingProvider


class FakeEmbedding(EmbeddingProvider):

    def embed(
        self,
        text: str,
    ) -> list[float]:

        return [1.0]


def test_retriever():

    store = VectorStore()

    store.add(
        VectorDocument(
            document_id="1",
            content="summary",
            embedding=[1.0],
        )
    )

    retriever = Retriever(
        FakeEmbedding(),
        store,
    )

    result = retriever.retrieve(RetrievalQuery("summary"))

    assert len(result) == 1
