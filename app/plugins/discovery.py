"""
Plugin discovery service.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from .loader import PluginLoader
from .plugin import Plugin


class PluginDiscovery:

    def __init__(
        self,
        directory: str,
    ) -> None:

        self.directory = Path(directory)

        self.loader = PluginLoader()

    def discover(
        self,
    ) -> list[Plugin]:

        plugins: list[Plugin] = []

        for file in self.directory.glob("*.py"):

            if file.name.startswith("_"):
                continue

            spec = importlib.util.spec_from_file_location(
                file.stem,
                file,
            )

            if spec is None:
                continue

            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)

            if hasattr(
                module,
                "PLUGIN_CLASS",
            ):

                plugin = module.PLUGIN_CLASS()

                plugins.append(plugin)

        return plugins
