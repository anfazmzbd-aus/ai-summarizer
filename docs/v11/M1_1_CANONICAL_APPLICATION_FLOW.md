# V11 M1.1 — Canonical Application Integration Boundary

## Status

Approved architecture implemented as a declarative boundary. Runtime behavior is
unchanged by M1.1.

## Canonical product endpoint

`POST /api/v1/summarize` is the canonical V11 product summarization endpoint.

`POST /summarize` remains a compatibility endpoint during V11 integration. It must
not evolve as an independent product path and may later delegate to the canonical
application service when compatibility behavior is preserved.

## Canonical ownership chain

The target V11 product path is:

```text
frontend
  -> app.routes.ai
  -> app.api.dependencies.build_summarization_application
  -> app.api.application.SummarizationApplication
  -> V9 SummarizationPipeline                 [M2]
  -> app.intelligence                         [M3]
  -> app.orchestration / app.runtime / app.distributed
  -> app.providers.runtime.ProviderRuntime
  -> response
  -> frontend