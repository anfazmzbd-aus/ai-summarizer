"""
Prompt template.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PromptTemplate:

    name: str

    version: str

    template: str

    metadata: dict[str, Any] = field(default_factory=dict)
