"""
Context builder.
"""

from __future__ import annotations

from .retrieval_result import RetrievalResult


class ContextBuilder:

    def build(
        self,
        results: list[RetrievalResult],
    ) -> str:

        return "\n\n".join(result.document.content for result in results)
