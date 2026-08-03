"""
Execution security context.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SecurityContext:

    authenticated: bool = True

    tenant_id: str | None = None

    origin: str | None = None
