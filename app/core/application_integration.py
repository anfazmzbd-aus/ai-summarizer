"""V11 canonical application integration boundary.

This module records the product-path ownership decisions established by
V11 M1.1. It is intentionally declarative: runtime wiring is introduced
by later V11 milestones without moving authority into the V10 intelligence
package or creating a parallel execution/provider stack.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationIntegrationBoundary:
    """Immutable ownership contract for the canonical V11 product path."""

    canonical_api_path: str
    compatibility_api_path: str
    canonical_route_module: str
    compatibility_route_module: str
    application_service_owner: str
    application_facade_owner: str
    summarization_pipeline_owner: str
    intelligence_owner: str
    execution_runtime_owners: tuple[str, ...]
    provider_runtime_owner: str

    @property
    def canonical_flow(self) -> tuple[str, ...]:
        """Return the ordered ownership chain for the V11 product path."""

        return (
            self.canonical_route_module,
            self.application_service_owner,
            self.application_facade_owner,
            self.summarization_pipeline_owner,
            self.intelligence_owner,
            *self.execution_runtime_owners,
            self.provider_runtime_owner,
        )


V11_APPLICATION_INTEGRATION_BOUNDARY = ApplicationIntegrationBoundary(
    canonical_api_path="/api/v1/summarize",
    compatibility_api_path="/summarize",
    canonical_route_module="app.routes.ai",
    compatibility_route_module="app.api.v1.summarize_endpoint",
    application_service_owner="app.api.application.build_summarization_application",
    application_facade_owner="app.api.application.SummarizationApplication",
    summarization_pipeline_owner="app.summarization.pipeline.SummarizationPipeline",
    intelligence_owner="app.intelligence",
    execution_runtime_owners=(
        "app.orchestration",
        "app.runtime",
        "app.distributed",
    ),
    provider_runtime_owner="app.providers.runtime.ProviderRuntime",
)
