"""
Retriever implementation.
"""

from __future__ import annotations

from app.memory.vector import (
    EmbeddingProvider,
    VectorStore,
)

from .retrieval_query import RetrievalQuery
from .retrieval_result import RetrievalResult


class Retriever:

    def __init__(
        self,
        embeddings: EmbeddingProvider,
        store: VectorStore,
    ) -> None:

        self._embeddings = embeddings
        self._store = store

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:

        embedding = self._embeddings.embed(query.text)

        documents = self._store.search(
            embedding,
            query.limit,
        )

        return [
            RetrievalResult(
                document=document,
                score=1.0,
            )
            for document in documents
        ]
