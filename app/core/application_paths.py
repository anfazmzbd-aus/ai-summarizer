"""V11 application-path inventory and convergence policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ApplicationPathRole(str, Enum):
    """Role assigned to an externally reachable summarization path."""

    CANONICAL = "canonical"
    COMPATIBILITY = "compatibility"


@dataclass(frozen=True)
class ApplicationPath:
    """Immutable description of a V11 summarization application path."""

    role: ApplicationPathRole
    api_path: str
    route_module: str
    composition_owner: str
    may_gain_product_behavior: bool


CANONICAL_SUMMARIZATION_PATH = ApplicationPath(
    role=ApplicationPathRole.CANONICAL,
    api_path="/api/v1/summarize",
    route_module="app.routes.ai",
    composition_owner="app.api.application.build_summarization_application",
    may_gain_product_behavior=True,
)


COMPATIBILITY_SUMMARIZATION_PATH = ApplicationPath(
    role=ApplicationPathRole.COMPATIBILITY,
    api_path="/summarize",
    route_module="app.api.v1.summarize_endpoint",
    composition_owner="app.services.summarize_service.SummarizeService",
    may_gain_product_behavior=False,
)


SUMMARIZATION_APPLICATION_PATHS = (
    CANONICAL_SUMMARIZATION_PATH,
    COMPATIBILITY_SUMMARIZATION_PATH,
)
