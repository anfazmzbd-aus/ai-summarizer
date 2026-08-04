"""
Runtime compatibility checks.
"""

from __future__ import annotations


class CompatibilityChecker:

    def compatible(
        self,
        runtime_version: str,
        required_version: str,
    ) -> bool:

        return runtime_version >= required_version
