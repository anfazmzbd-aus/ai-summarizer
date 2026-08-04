"""
Retrieval result.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.memory.vector import VectorDocument


@dataclass(slots=True)
class RetrievalResult:

    document: VectorDocument

    score: float
