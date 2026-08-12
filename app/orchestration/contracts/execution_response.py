"""
AI Summarizer V9.1

Execution response contract.

Provides the complete execution response returned by
the V9 application/runtime pipeline while retaining
dictionary-style compatibility for legacy service consumers.
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ExecutionResponse(BaseModel):
    """
    Complete execution response contract.

    The canonical representation is the typed Pydantic model.

    Dictionary-style access is retained for compatibility:

        response["summary"]

    resolves to:

        response.result["summary"]
    """

    execution_id: str

    status: str = "success"

    result: Dict[str, Any] = Field(
        default_factory=dict,
    )

    node_outputs: Dict[str, Any] = Field(
        default_factory=dict,
    )

    trace: List[Dict[str, Any]] = Field(
        default_factory=list,
    )

    metrics: Dict[str, Any] = Field(
        default_factory=dict,
    )

    errors: List[str] = Field(
        default_factory=list,
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
    )

    def __getitem__(self, key: str) -> Any:
        """
        Provide backward-compatible dictionary-style access.

        Result fields are exposed directly:

            response["summary"]

        Top-level execution fields remain accessible as well:

            response["execution_id"]
            response["status"]
            response["trace"]
            response["metrics"]
            response["errors"]
            response["metadata"]
            response["node_outputs"]
        """

        if key in self.result:
            return self.result[key]

        return getattr(self, key)

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Dictionary-compatible get() access.
        """

        if key in self.result:
            return self.result[key]

        return getattr(
            self,
            key,
            default,
        )

    def __contains__(self, key: str) -> bool:
        """
        Support:

            "summary" in response
        """

        return key in self.result or hasattr(
            self,
            key,
        )
