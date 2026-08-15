"""
Context-preserving aggregation for summarization strategies.
"""

from .aggregator import ContextAggregator
from .models import AggregatedContext, ContextEnvelope

__all__ = [
    "AggregatedContext",
    "ContextAggregator",
    "ContextEnvelope",
]
