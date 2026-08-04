"""
Plugin registry.
"""

from __future__ import annotations

from .plugin import Plugin


class PluginRegistry:

    def __init__(self) -> None:

        self._plugins: dict[str, Plugin] = {}

    def add(
        self,
        plugin: Plugin,
    ) -> None:

        self._plugins[plugin.metadata.name] = plugin

    def get(
        self,
        name: str,
    ) -> Plugin | None:

        return self._plugins.get(name)

    def all(
        self,
    ) -> list[Plugin]:

        return list(self._plugins.values())

    def count(
        self,
    ) -> int:

        return len(self._plugins)
