"""
V9.3-M9 intelligent streaming integration.

Adds deterministic intelligence provenance to the existing V9.2
provider-independent streaming contract without modifying the underlying
streaming primitives.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

from .events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)
from .models import StreamResult
from .streamer import SummarizationStreamer


@dataclass(frozen=True)
class IntelligentStreamContext:
    """
    Immutable intelligence context attached to a streaming execution.

    The context deliberately uses provider-independent metadata rather
    than importing planner, evaluator, optimizer, or resilience classes.
    This prevents cross-layer coupling while preserving provenance from
    V9.3-M1 through M8.
    """

    planner: Mapping[str, Any] = field(default_factory=dict)
    document: Mapping[str, Any] = field(default_factory=dict)
    intent: Mapping[str, Any] = field(default_factory=dict)
    adaptive: Mapping[str, Any] = field(default_factory=dict)
    optimization: Mapping[str, Any] = field(default_factory=dict)
    quality: Mapping[str, Any] = field(default_factory=dict)
    resilience: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        fields = (
            ("planner", self.planner),
            ("document", self.document),
            ("intent", self.intent),
            ("adaptive", self.adaptive),
            ("optimization", self.optimization),
            ("quality", self.quality),
            ("resilience", self.resilience),
        )

        for name, value in fields:
            if not isinstance(value, Mapping):
                raise TypeError(f"{name} must be a mapping")

    def to_metadata(self) -> dict[str, Any]:
        """
        Return a deterministic metadata representation.

        Each intelligence layer receives its own namespace so metadata
        provenance remains unambiguous.
        """

        return {
            "intelligence": {
                "planner": dict(self.planner),
                "document": dict(self.document),
                "intent": dict(self.intent),
                "adaptive": dict(self.adaptive),
                "optimization": dict(self.optimization),
                "quality": dict(self.quality),
                "resilience": dict(self.resilience),
            }
        }


class IntelligentSummarizationStreamer:
    """
    V9.3-M9 adapter around the existing V9.2 SummarizationStreamer.

    No provider, transport, execution engine, or LLM dependency is
    introduced.

    Existing V9.2 event types and ordering remain unchanged.
    """

    streamer_version = "v9.3-m9"

    def __init__(
        self,
        streamer: SummarizationStreamer | None = None,
    ) -> None:
        self._streamer = streamer or SummarizationStreamer()

    def stream(
        self,
        source: Iterable[str],
        *,
        context: IntelligentStreamContext | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Iterator[
        (
            StreamStartedEvent
            | StreamChunkEvent
            | StreamCompletedEvent
            | StreamErrorEvent
        )
    ]:
        """
        Stream existing V9.2 lifecycle events with M9 intelligence metadata.

        Explicit metadata remains supported for compatibility and is
        merged with the intelligence namespace.
        """

        if metadata is not None and not isinstance(
            metadata,
            Mapping,
        ):
            raise TypeError("metadata must be a mapping")

        stream_metadata: dict[str, Any] = dict(metadata or {})

        stream_metadata["streaming"] = {
            "streamer_version": self.streamer_version,
            "intelligent": True,
        }

        if context is not None:
            if not isinstance(
                context,
                IntelligentStreamContext,
            ):
                raise TypeError("context must be an IntelligentStreamContext")

            stream_metadata.update(context.to_metadata())

        yield from self._streamer.stream(
            source,
            metadata=stream_metadata,
        )

    def collect(
        self,
        source: Iterable[str],
        *,
        context: IntelligentStreamContext | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> StreamResult:
        """
        Consume an intelligent stream and return the existing V9.2
        StreamResult contract.
        """

        events = self.stream(
            source,
            context=context,
            metadata=metadata,
        )

        content_parts: list[str] = []
        chunk_count = 0

        for event in events:
            if isinstance(
                event,
                StreamChunkEvent,
            ):
                content_parts.append(event.content)
                chunk_count += 1

            elif isinstance(
                event,
                StreamErrorEvent,
            ):
                raise RuntimeError(f"{event.error_type}: {event.message}")

            elif isinstance(
                event,
                StreamCompletedEvent,
            ):
                return StreamResult(
                    content=event.content,
                    chunk_count=event.chunk_count,
                    metadata=dict(event.metadata),
                )

        raise RuntimeError("stream ended without a completion event")


__all__ = [
    "IntelligentStreamContext",
    "IntelligentSummarizationStreamer",
]
