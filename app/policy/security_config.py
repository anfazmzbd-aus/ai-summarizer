"""
Security policy configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class SecurityConfig:

    allowed_agent_types: set[str] = field(default_factory=set)

    allowed_origins: set[str] = field(default_factory=set)

    require_tenant_id: bool = False

    require_authenticated: bool = False
