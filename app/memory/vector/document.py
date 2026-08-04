"""
Vector document model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VectorDocument:

    document_id: str

    content: str

    embedding: list[float]

    metadata: dict[str, Any] = field(default_factory=dict)
