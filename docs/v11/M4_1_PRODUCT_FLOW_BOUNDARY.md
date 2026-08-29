# V11 M4.1 Product Flow Boundary

## Scope

M4.1 audits the current product entry points and establishes the boundary for
the later frontend/API integration increments. It does not redesign the
frontend, change compatibility behavior, or add M4.2+ functionality.

## Current product flow

The current V11 API product path is:

```text
POST /api/v1/summarize
  -> app.routes.ai.summarize
  -> app.api.application.build_summarization_application()
  -> app.api.application.SummarizationApplication
  -> AsyncSummarizationPipelineAdapter
  -> existing V9 SummarizationPipeline
  -> existing service/provider callback
  -> SummarizeResponse
```

The route accepts user text plus provider/model selections and returns the
public summary and token-usage fields. M3 application metadata remains inside
the application result boundary and is not independently exposed by this API
response.

## Frontend audit

There is no frontend route or static frontend mounted by the current
`app/main.py`. The only summarization form in the repository is the archived
`app/legacy/v7.6/templates/index.html`; it posts to compatibility
`POST /summarize`. That template is therefore a known product-path divergence,
not evidence that the V11 frontend uses the canonical endpoint.

The compatibility endpoint remains independently implemented by
`app/api/v1/summarize_endpoint.py` and does not use the V11 application
boundary. This is preserved intentionally for compatibility and is outside the
M4.1 correction scope.

## M4.1 boundary and evidence

M4.1 establishes these invariants:

- canonical user-facing API behavior is tested through
  `POST /api/v1/summarize`;
- realistic deterministic text reaches the canonical application and existing
  V9 pipeline;
- the compatibility `/summarize` route remains distinct and does not acquire
  V11 application behavior;
- no live provider is required;
- frontend migration to the canonical endpoint is deferred to M4.2.

No production-code defect was found in the canonical API/application wiring,
so no production source file is changed in M4.1.
