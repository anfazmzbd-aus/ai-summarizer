"""
Vector store abstraction.
"""

from __future__ import annotations

from .document import VectorDocument
from .similarity import cosine_similarity


class VectorStore:

    def __init__(self) -> None:

        self._documents: dict[
            str,
            VectorDocument,
        ] = {}

    def add(
        self,
        document: VectorDocument,
    ) -> None:

        self._documents[document.document_id] = document

    def get(
        self,
        document_id: str,
    ) -> VectorDocument | None:

        return self._documents.get(document_id)

    def search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[VectorDocument]:

        ranked = sorted(
            self._documents.values(),
            key=lambda document: cosine_similarity(
                embedding,
                document.embedding,
            ),
            reverse=True,
        )

        return ranked[:limit]

    def count(
        self,
    ) -> int:

        return len(self._documents)
