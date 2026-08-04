"""
Plugin capability metadata.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CapabilityInfo:

    name: str

    version: str

    plugin: str

    description: str = ""
