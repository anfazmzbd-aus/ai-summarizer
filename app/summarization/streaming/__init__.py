"""
Provider-independent streaming primitives for summarization.
"""

from .events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)
from .models import (
    StreamEventType,
    StreamResult,
)
from .streamer import SummarizationStreamer

__all__ = [
    "StreamChunkEvent",
    "StreamCompletedEvent",
    "StreamErrorEvent",
    "StreamEventType",
    "StreamResult",
    "StreamStartedEvent",
    "SummarizationStreamer",
]
