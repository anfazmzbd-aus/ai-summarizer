"""
Plugin validator.
"""

from __future__ import annotations

from .compatibility import CompatibilityChecker
from .plugin import Plugin


class PluginValidator:

    def __init__(
        self,
        runtime_version: str,
    ) -> None:

        self._runtime = runtime_version
        self._checker = CompatibilityChecker()

    def validate(
        self,
        plugin: Plugin,
        required_version: str,
    ) -> bool:

        return self._checker.compatible(
            self._runtime,
            required_version,
        )
