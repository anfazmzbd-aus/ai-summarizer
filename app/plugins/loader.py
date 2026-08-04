"""
Plugin loader.
"""

from __future__ import annotations

import importlib

from .plugin import Plugin


class PluginLoader:

    def load(
        self,
        module_name: str,
    ) -> Plugin:

        module = importlib.import_module(module_name)

        plugin_class = getattr(
            module,
            "PLUGIN_CLASS",
        )

        plugin = plugin_class()

        if not isinstance(
            plugin,
            Plugin,
        ):
            raise TypeError("Invalid plugin type.")

        return plugin
