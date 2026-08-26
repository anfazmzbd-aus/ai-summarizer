# V11 M1.3 — Application Path Inventory and Convergence Guardrails

## Objective

Record the externally reachable summarization paths present at the V11
integration baseline and prevent them from evolving as independent products.

## Canonical path

```text
POST /api/v1/summarize
  -> app.routes.ai
  -> build_summarization_application()
  -> SummarizationApplication