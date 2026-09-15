# V13 M1 — Product Contracts and Architecture Foundation

## Status

COMPLETE

## Objective

Establish product-facing summarization controls while preserving the
certified V12 application architecture.

## Product Contract

Supported summary types:

- general
- executive
- key_points
- action_items
- findings
- insights
- technical

Supported summary lengths:

- short
- medium
- detailed

Optional user instructions:

- whitespace normalized
- maximum 2,000 characters
- no silent truncation

## Backward Compatibility

Existing V12 requests remain valid.

Requests without V13 fields resolve to:

- summary_type: general
- summary_length: medium
- instructions: none

## Prompt Contract

Canonical V13 application:

summary:2.0.0

Legacy direct runtime requests retain:

summary:1.0 default

Prompt version selection is explicit through AIRuntimeRequest.

## Architecture

HTTP/API
→ SummarizationApplication
→ product-option resolution
→ bounded intelligence
→ V9 summarization pipeline
→ SummarizationService
→ AI runtime/provider

## Preserved Invariants

- canonical application boundary preserved
- V9 summarization pipeline preserved
- V10 bounded intelligence preserved
- provider architecture preserved
- fake provider remains default
- OpenRouter remains OpenAI-compatible configuration
- no frontend product logic introduced
- no persistence introduced
- no file ingestion introduced
- no provider expansion introduced

## Certification

- targeted API tests: PASS
- product-option tests: PASS
- runtime prompt-version tests: PASS
- architecture tests: PASS
- provider integration tests: PASS
- full non-live regression: PASS
- Black: PASS
- Ruff: PASS
- git diff --check: PASS

## M1 Result

V13 product contract and architecture foundation approved for frontend
development.