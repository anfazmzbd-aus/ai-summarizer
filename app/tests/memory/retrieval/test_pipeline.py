from app.memory import (
    ContextBuilder,
    RetrievalPipeline,
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


def test_pipeline():

    store = VectorStore()

    store.add(
        VectorDocument(
            document_id="1",
            content="Knowledge Item",
            embedding=[1.0],
        )
    )

    pipeline = RetrievalPipeline(
        Retriever(
            FakeEmbedding(),
            store,
        ),
        ContextBuilder(),
    )

    context = pipeline.run(RetrievalQuery("knowledge"))

    assert "Knowledge Item" in context
