"""
Plugin lifecycle manager.
"""

from __future__ import annotations

from .plugin import Plugin
from .plugin_state import PluginState
from .context import PluginContext


class PluginLifecycle:

    def __init__(
        self,
        plugin: Plugin,
    ) -> None:

        self.plugin = plugin

        self.state = PluginState.REGISTERED

    def initialize(
        self,
        context: PluginContext,
    ) -> None:

        self.plugin.initialize(context)

        self.state = PluginState.INITIALIZED

    def activate(
        self,
    ) -> None:

        self.state = PluginState.ACTIVE

    def stop(
        self,
    ) -> None:

        self.plugin.shutdown()

        self.state = PluginState.STOPPED
