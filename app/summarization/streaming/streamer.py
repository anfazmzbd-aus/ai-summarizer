"""
Deterministic provider-independent summarization streamer.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from .events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)
from .models import StreamResult


class SummarizationStreamer:
    """
    Convert an iterable of text fragments into a deterministic stream
    of lifecycle events.

    The class does not know anything about LLM providers, FastAPI, or
    network transport.
    """

    def stream(
        self,
        source: Iterable[str],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[
        (
            StreamStartedEvent
            | StreamChunkEvent
            | StreamCompletedEvent
            | StreamErrorEvent
        )
    ]:
        """
        Yield streaming lifecycle events.

        The source is consumed lazily. The method therefore supports
        lists, tuples, generators, and other iterables.
        """
        if isinstance(source, (str, bytes)):
            raise TypeError(
                "source must be an iterable of text fragments, "
                "not a string or bytes object"
            )

        if not isinstance(source, Iterable):
            raise TypeError("source must be iterable")

        stream_metadata = dict(metadata or {})

        yield StreamStartedEvent(
            metadata=stream_metadata,
        )

        sequence = 0
        parts: list[str] = []

        try:
            for fragment in source:
                if not isinstance(fragment, str):
                    raise TypeError("stream fragments must be strings")

                parts.append(fragment)

                yield StreamChunkEvent(
                    sequence=sequence,
                    content=fragment,
                    metadata={
                        **stream_metadata,
                        "sequence": sequence,
                    },
                )

                sequence += 1

        except Exception as exc:
            yield StreamErrorEvent(
                error_type=type(exc).__name__,
                message=str(exc),
                sequence=sequence,
                metadata=stream_metadata,
            )
            return

        content = "".join(parts)

        yield StreamCompletedEvent(
            content=content,
            chunk_count=sequence,
            metadata=stream_metadata,
        )

    def collect(
        self,
        source: Iterable[str],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> StreamResult:
        """
        Consume a complete stream and return its reconstructed result.

        A stream error raises RuntimeError rather than silently returning
        partial content.
        """
        content_parts: list[str] = []
        chunk_count = 0

        for event in self.stream(
            source,
            metadata=metadata,
        ):
            if isinstance(event, StreamChunkEvent):
                content_parts.append(event.content)
                chunk_count += 1

            elif isinstance(event, StreamErrorEvent):
                raise RuntimeError(f"{event.error_type}: {event.message}")

            elif isinstance(event, StreamCompletedEvent):
                return StreamResult(
                    content=event.content,
                    chunk_count=event.chunk_count,
                    metadata=dict(event.metadata),
                )

        raise RuntimeError("stream ended without a completion event")


__all__ = ["SummarizationStreamer"]
