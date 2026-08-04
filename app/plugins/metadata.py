"""
Plugin metadata.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PluginMetadata:

    name: str

    version: str

    author: str = ""

    description: str = ""
