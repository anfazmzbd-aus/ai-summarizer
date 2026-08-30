# V11 M4.4 Product Contract Integration

The canonical `POST /api/v1/summarize` response now contains the stable
product fields `summary`, `model`, `prompt_tokens`, `completion_tokens`, and
`total_tokens`, plus a product-safe `metadata` object.

Metadata projects only existing descriptive application values: strategy,
chunk count, intelligence mode, trace ID, explainability summary, and the
existing observability/diagnostic values. Internal V9 pipeline objects, V10
domain objects, provider details, authority state, and arbitrary attributes do
not cross the HTTP boundary. Missing optional values serialize as `null`.

Canonical application failures use a stable error envelope under `detail`:

- `409 REVIEW_REQUIRED` when execution must stop for review;
- `422 INVALID_APPLICATION_STATE` for invalid authority/application state;
- `500 SUMMARIZATION_FAILED` for deterministic execution failures.

Messages are product-safe and do not expose raw exception text or stack traces.
The supported frontend reads the canonical error message and continues to call
only `/api/v1/summarize`. Compatibility `/summarize` remains unchanged.

The application façade, V9 pipeline ownership, V10 bounded authority, and
read-only observability boundaries are preserved. M4.5+ intelligence scenarios,
streaming, resilience, performance, provider redesign, and authentication are
deferred.
