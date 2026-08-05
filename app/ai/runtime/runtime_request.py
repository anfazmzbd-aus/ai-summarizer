"""
AI runtime request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIRuntimeRequest:

    provider: str

    prompt_name: str

    model: str

    variables: dict[str, Any] = field(default_factory=dict)
