# V11 M4.3 Real-Text Scenarios

M4.3 validates deterministic realistic English text through the canonical
product API:

```text
POST /api/v1/summarize
  -> SummarizationApplication
  -> existing V9 pipeline
  -> deterministic service
  -> product response
```

The focused scenarios use locally generated repeated prose and the existing
V9 defaults:

- short text: `DIRECT`;
- medium text: `MAP_REDUCE`;
- long text: `HIERARCHICAL`.

Tests assert strategy and chunk information through the application’s existing
read-only metadata boundary, and verify valid response/token accounting plus
provider/model propagation. No live provider is used. V9 remains the owner of
chunking and strategy behavior; no V9 redesign, V10 authority change,
streaming, resilience, performance, or M4.4+ behavior is introduced.
