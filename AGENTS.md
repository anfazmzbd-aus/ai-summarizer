# Repository Guidelines

## Project identity and current release program

This repository is the AI Summarizer standalone application.

Frozen major baselines:

- V10.0.0 — Bounded Intelligence Architecture — COMPLETE and FROZEN
- V11.0.0 — Canonical Full-System Integration — COMPLETE and FROZEN
- V12.0.0 — Production Certification / Standalone Release — COMPLETE and FROZEN
- V13.0.0 — Product Experience & Release Certification — IN PROGRESS

The certified M9.2-M9.8 release-candidate identity is `13.0.0-rc1`. During M9.9 the active application identity is `13.0.0` while final artifact and remote release certification are completed.

## Current authoritative repository state

Development continues in `E:\Projects\ai-summarizer` on `main`. Do not relocate the repository for normal development. Before editing, verify `git status`, `git log -5 --oneline --decorate`, and `git rev-parse HEAD`.

Frozen V13 checkpoints include M1 through M8. M8 is tag `v13.0.0-m8` at commit `424deed36dbeba9e6acb619653e75c9d25cc3dd6`. The M9.2-M9.4 release-candidate identity/packaging checkpoint is commit `0ef2b7f95a6e4f65e9a7376cc18fc7fff894f602`. Do not move frozen tags.

## Architecture ownership

- V7 owns execution graph/scheduling/executor/orchestration architecture.
- V8 owns distributed runtime, workers, queues, retry/recovery, policy and telemetry infrastructure.
- V9 owns provider abstraction, prompts, summarization pipeline, chunking, hierarchical/map-reduce/context strategies and streaming.
- V10 owns bounded intelligence and authority contracts.
- V11 owns canonical product integration across those systems.
- V12 owns production certification and standalone release hardening.
- V13 owns the practical product surface and product release certification while preserving those boundaries.

Do not create a second summarization pipeline, another provider abstraction, a parallel runtime, or a new intelligence subsystem.

## Canonical V13 product path

```text
Frontend / product API
  -> app.routes.ai
  -> app.api.application.SummarizationApplication
  -> bounded intelligence
  -> AsyncSummarizationPipelineAdapter
  -> existing V9 SummarizationPipeline
  -> runtime/provider boundary
  -> product-safe response + metadata
```

File extraction normalizes TXT/PDF content and returns it to the same canonical summarization path. It must not become a second summarization path.

## Locked authority invariants

PRESERVE and ADVISORY have no execution-change authority. CONSTRAINED has bounded authority only. REVIEW has no execution-change authority and requires review. Rejected directives cannot cross the handoff. Missing/insufficient evidence defaults toward PRESERVE. Invalid architecture state fails closed. Provenance is not silently rewritten. Observability/explainability remain read-only. Provider/runtime details remain outside core intelligence contracts.

## V13 scope

V13 MVP includes paste text, TXT/PDF ingestion, summary type/length controls, approved product-model selection, custom instructions, truthful processing/errors, result copy/TXT download/regenerate, safe processing details, responsive behavior and accessibility.

Deferred/excluded: DOCX, OCR, history, authentication/accounts, persistence, advanced analytics, PDF/DOCX export, arbitrary provider selection, new provider architecture, new intelligence/distributed architecture, native mobile, and major deployment redesign.

## Current milestone

M9.1-M9.8 are complete/certified. M9.9 pre-publication certification is complete; exact final artifact and local/remote v13.0.0 release-identity certification remain. No new features are permitted in M9.

Any source change after certification evidence requires defect classification, the smallest correction, affected certification rerun, full non-live regression, and recertification.

## Validation gates

Focused tests first, then affected subsystem tests, then:

```powershell
pytest -m "not live" -q
pre-commit run --all-files
git diff --check
git status
```

Live tests remain explicitly marked `live` and require deliberate `--run-live`/approved execution. Do not spend provider credits during routine validation.

Latest M9.9 non-live baseline: `5373 passed, 10 deselected`.

## Python environment

The established development environment is `E:\Projects\ai-summarizer\venv311` using Python 3.11. Do not replace it or install project dependencies into system Python without explicit approval.

## Git discipline

Use explicit staging. Never commit `.env`, credentials, API keys, virtual environments, caches, runtime databases, generated `dist/` artifacts, or unrelated workspace state. Do not rewrite frozen release tags.

## Security

Never commit or print secrets. Provider credentials come from the runtime environment. Product-facing errors must not expose credentials or sensitive internal diagnostics. Unsupported provider/configuration state fails closed.

## Agent operating rule

Before a milestone change: inspect current implementation/tests, state the minimal plan, preserve frozen architecture, implement incrementally, run focused validation, run full non-live regression, run quality gates, and report exact changed files/results. Do not weaken architecture tests to force a change through.
