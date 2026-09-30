# AI Summarizer V13.0.0 — Release Notes

## Release Program

```text
Product: AI Summarizer
Release: V13.0.0
Current candidate identity: 13.0.0-rc1
Current phase: M9.8 — Release Candidate Certification
Final release status: NOT YET PUBLISHED
```

V13 converts the certified standalone application into a practical, polished user product while preserving the canonical architecture established through V11 and certified in V12.

## Product Capabilities

V13 adds a responsive browser experience; paste-text and TXT/PDF ingestion; General, Executive, Key Points, Action Items, Findings, Insights, and Technical summary types; Short, Medium, and Detailed lengths; approved product-model selection; custom instructions; truthful processing/error states; Copy, UTF-8 TXT Download, Regenerate; safe processing details; and accessibility hardening.

## Architecture

```text
Frontend / product API
  -> canonical SummarizationApplication
  -> bounded intelligence
  -> V9 summarization pipeline
  -> runtime/provider boundary
  -> product-safe response + metadata
```

No second summarization path, provider abstraction, runtime, or intelligence subsystem is introduced. File extraction rejoins the canonical summarization flow.

## Providers

Certified provider values remain `fake` and `openai`. OpenRouter is used through the OpenAI-compatible `openai` provider configuration with an appropriate base URL, credential, and model. `AI_PROVIDER=openrouter` is not supported.

## File Ingestion

TXT and PDF are supported up to 10 MiB. TXT is normalized from UTF-8/BOM input. Encrypted PDFs and PDFs without extractable text are rejected. DOCX and OCR are outside scope. Extraction does not auto-summarize.

## Result Workspace

Successful results can be copied, downloaded as UTF-8 TXT, regenerated with current source/controls, and inspected through collapsed processing details. Malformed/blank successful HTTP payloads are not accepted as valid summaries. Existing successful results are preserved across applicable failure states.

## Accessibility and Hardening

V13 includes keyboard-focus treatment, semantic result/status regions, action grouping, responsive layouts, reduced-motion handling, and failure/recovery hardening validated during M8.

## Release Certification

M9.1-M9.3 established release baseline, RC identity, and final functional/regression certification. M9.4 certified deterministic packaging after correcting the V13 documentation allowlist. M9.5 certified clean installation, application/runtime imports, HTTP startup, browser operation, TXT/PDF ingestion, and runtime validation. M9.6 certified one controlled real-provider execution through the canonical OpenAI-compatible path and then restored the offline baseline.

Latest post-live non-live regression: `5372 passed, 10 deselected`.

## Distribution

Release candidate: `ai-summarizer-v13.0.0-rc1.zip`. Final release: `ai-summarizer-v13.0.0.zip`. Certified artifacts are accompanied by SHA-256 checksums. The final RC artifact/checksum will be rebuilt after M9.7 documentation changes and certified during M9.8.

## Scope Boundaries

V13 does not add DOCX/OCR, history, accounts/authentication, persistence, advanced analytics, PDF/DOCX export, arbitrary provider selection, new provider/intelligence/distributed architecture, native mobile, or major deployment redesign.

## Status

M9.7 is complete. M9.8 release-candidate certification is next. M9.9 final `v13.0.0` publication remains pending. No final-release claim is valid until M9.8 and M9.9 complete.
