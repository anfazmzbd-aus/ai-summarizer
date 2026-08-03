"""
Dependency providers.
"""

from __future__ import annotations

from .container import ObservabilityContainer

_container = ObservabilityContainer()


def get_observability() -> ObservabilityContainer:

    return _container
