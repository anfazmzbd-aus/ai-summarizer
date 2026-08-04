"""
Plugin capability definitions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AgentCapability:

    name: str

    version: str

    description: str = ""
