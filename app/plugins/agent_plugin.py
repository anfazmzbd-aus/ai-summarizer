"""
Agent plugin contract.
"""

from __future__ import annotations

from abc import abstractmethod

from .plugin import Plugin
from .capability import AgentCapability


class AgentPlugin(Plugin):

    @property
    @abstractmethod
    def capability(
        self,
    ) -> AgentCapability: ...

    @abstractmethod
    def create_agent(
        self,
    ): ...
