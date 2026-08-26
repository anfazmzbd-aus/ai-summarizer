# V11 M1.2 — Canonical Application Composition

## Status

Implementation milestone.

## Objective

Introduce a stable application-level composition boundary for the canonical
V11 summarization API without changing existing V10 summarization behavior.

## Canonical runtime entry

```text
POST /api/v1/summarize
        |
        v
app.routes.ai
        |
        v
build_summarization_application()
        |
        v
SummarizationApplication
        |
        v
existing app.ai.SummarizationService