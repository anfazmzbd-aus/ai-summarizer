"""
Plugin manager.
"""

from __future__ import annotations

from .context import PluginContext
from .plugin import Plugin


class PluginManager:

    def __init__(self) -> None:

        self._plugins: dict[str, Plugin] = {}

    def register(
        self,
        plugin: Plugin,
    ) -> None:

        name = plugin.metadata.name

        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' already registered.")

        self._plugins[name] = plugin

    def initialize_all(
        self,
        context: PluginContext,
    ) -> None:

        for plugin in self._plugins.values():
            plugin.initialize(context)

    def shutdown_all(
        self,
    ) -> None:

        for plugin in self._plugins.values():
            plugin.shutdown()

    def plugins(
        self,
    ) -> list[Plugin]:

        return list(self._plugins.values())

    def count(
        self,
    ) -> int:

        return len(self._plugins)
