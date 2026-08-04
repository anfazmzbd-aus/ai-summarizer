"""
Capability registry.
"""

from __future__ import annotations

from .capability_info import CapabilityInfo


class CapabilityRegistry:

    def __init__(self) -> None:

        self._capabilities: dict[str, CapabilityInfo] = {}

    def register(
        self,
        capability: CapabilityInfo,
    ) -> None:

        self._capabilities[capability.name] = capability

    def get(
        self,
        name: str,
    ) -> CapabilityInfo | None:

        return self._capabilities.get(name)

    def all(
        self,
    ) -> list[CapabilityInfo]:

        return list(self._capabilities.values())

    def count(
        self,
    ) -> int:

        return len(self._capabilities)
