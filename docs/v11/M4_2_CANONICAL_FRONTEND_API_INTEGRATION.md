# V11 M4.2 Canonical Frontend/API Integration

## Scope

M4.2 establishes the supported frontend entry point and connects it to the
canonical V11 API. It does not redesign styling, alter the compatibility
endpoint, add streaming or resilience behavior, or validate live providers.

## Supported product flow

```text
GET /
  -> app.routes.frontend
  -> app/templates/index.html
  -> /static/app.js
  -> POST /api/v1/summarize
  -> app.routes.ai
  -> SummarizationApplication
```

The frontend sends the entered text to `/api/v1/summarize` with the existing
deterministic `fake` provider and `demo` model defaults. The archived
`app/legacy/v7.6` template remains unchanged and the compatibility
`/summarize` route remains outside the V11 application path.

## M4.2 boundary

- The supported page is mounted at `GET /`.
- Existing root `static/style.css` is reused without a styling redesign.
- `static/app.js` calls only `/api/v1/summarize`.
- The frontend displays the canonical response summary and reports request
  failures without introducing a second execution path.
- Tests are offline and use the existing deterministic provider configuration.

M4.3 real-text scenario expansion and later streaming, provider, resilience,
performance, and product-response work remain out of scope.
