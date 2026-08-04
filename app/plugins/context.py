"""
Plugin execution context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PluginContext:

    services: dict[str, Any] = field(default_factory=dict)

    configuration: dict[str, Any] = field(default_factory=dict)
