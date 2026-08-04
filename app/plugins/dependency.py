"""
Plugin dependency declaration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PluginDependency:

    name: str

    minimum_version: str
