"""
Knowledge graph relationship.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GraphRelationship:

    source: str

    target: str

    relation: str

    properties: dict[str, Any] = field(default_factory=dict)
