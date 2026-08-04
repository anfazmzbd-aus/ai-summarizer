"""
Knowledge graph entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GraphEntity:

    entity_id: str

    entity_type: str

    properties: dict[str, Any] = field(default_factory=dict)
