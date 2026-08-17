"""
Provider-independent streaming primitives for summarization.
"""

from .events import (
    StreamChunkEvent,
    StreamCompletedEvent,
    StreamErrorEvent,
    StreamStartedEvent,
)
from .intelligence import (
    IntelligentStreamContext,
    IntelligentSummarizationStreamer,
)
from .models import (
    StreamEventType,
    StreamResult,
)
from .streamer import SummarizationStreamer

__all__ = [
    "IntelligentStreamContext",
    "IntelligentSummarizationStreamer",
    "StreamChunkEvent",
    "StreamCompletedEvent",
    "StreamErrorEvent",
    "StreamEventType",
    "StreamResult",
    "StreamStartedEvent",
    "SummarizationStreamer",
]
