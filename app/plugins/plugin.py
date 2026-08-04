"""
Plugin contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .context import PluginContext
from .metadata import PluginMetadata


class Plugin(ABC):

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata: ...

    @abstractmethod
    def initialize(
        self,
        context: PluginContext,
    ) -> None: ...

    @abstractmethod
    def shutdown(
        self,
    ) -> None: ...
