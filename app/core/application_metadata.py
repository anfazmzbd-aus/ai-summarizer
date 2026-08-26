"""V11 read-only application integration metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class SummarizationExecutionMetadata:
    """
    Read-only product-path metadata.

    Metadata is descriptive only and must never become an execution
    authority channel.
    """

    strategy: str | None = None
    chunk_count: int | None = None
    intelligence_mode: str | None = None
    trace_id: str | None = None
    explainability_summary: str | None = None
    attributes: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(dict(self.attributes)),
        )
