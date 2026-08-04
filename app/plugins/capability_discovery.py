"""
Capability discovery.
"""

from __future__ import annotations

from .capability_registry import CapabilityRegistry
from .manager import PluginManager
from .agent_plugin import AgentPlugin
from .capability_info import CapabilityInfo


class CapabilityDiscovery:

    def discover(
        self,
        manager: PluginManager,
    ) -> CapabilityRegistry:

        registry = CapabilityRegistry()

        for plugin in manager.plugins():

            if not isinstance(
                plugin,
                AgentPlugin,
            ):
                continue

            capability = plugin.capability

            registry.register(
                CapabilityInfo(
                    name=capability.name,
                    version=capability.version,
                    plugin=plugin.metadata.name,
                    description=capability.description,
                )
            )

        return registry
