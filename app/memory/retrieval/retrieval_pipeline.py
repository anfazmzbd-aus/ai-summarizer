"""
Retrieval pipeline.
"""

from __future__ import annotations

from .context_builder import ContextBuilder
from .retrieval_query import RetrievalQuery
from .retriever import Retriever


class RetrievalPipeline:

    def __init__(
        self,
        retriever: Retriever,
        builder: ContextBuilder,
    ) -> None:

        self._retriever = retriever
        self._builder = builder

    def run(
        self,
        query: RetrievalQuery,
    ) -> str:

        results = self._retriever.retrieve(query)

        return self._builder.build(results)
