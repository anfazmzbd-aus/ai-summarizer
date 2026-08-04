"""
Loads agent plugins into runtime.
"""

from __future__ import annotations

from .agent_plugin import AgentPlugin


class AgentPluginLoader:

    def __init__(
        self,
    ) -> None:

        self._agents = {}

    def register(
        self,
        plugin: AgentPlugin,
    ) -> None:

        capability = plugin.capability

        self._agents[capability.name] = plugin.create_agent()

    def get(
        self,
        name: str,
    ):

        return self._agents.get(name)

    def count(
        self,
    ) -> int:

        return len(self._agents)
