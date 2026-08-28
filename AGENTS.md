# Repository Guidelines

## Project identity and completion roadmap

This repository is the AI Summarizer standalone application.

The master roadmap is locked:

- V10.0.0 — Bounded Intelligence Architecture — COMPLETE and FROZEN
- V11 — Full-System Integration & Product Hardening — IN PROGRESS
- V12.0.0 — Production Certification / Final Standalone Application — FUTURE

Do not introduce another major version before V12 unless an unavoidable technical requirement is discovered and explicitly approved.

## Current authoritative repository state

Development continues in the existing local repository:

`E:\Projects\ai-summarizer`

Do not clone, copy, archive-extract, or relocate the repository for normal development.

Current branch:

`main`

Frozen checkpoints:

- V10.0.0: tag `v10.0.0`, commit `f834090ec9b00eee41ea6c65ef6eb5dd5105793c`
- V11 M1: tag `v11.0.0-m1`, commit `578a80134310a502eaa2edcde7a4a5546d8553ea`
- V11 M2: tag `v11.0.0-m2`, commit `627bb730157d9d42d2ff78abce13a9660dd6c14b`

V11 M2 is the starting point for Codex-owned continuation.

Before editing, always verify:

```powershell
git status
git log -5 --oneline --decorate
git rev-parse HEAD
```

Expected starting HEAD for M3:

`627bb730157d9d42d2ff78abce13a9660dd6c14b`

If the repository is not clean or HEAD differs unexpectedly, stop and inspect before modifying source.

## Architecture ownership

Preserve the established architecture rather than creating parallel implementations.

### V7
Owns execution graph, scheduling, executor architecture, orchestration.

### V8
Owns distributed runtime, workers, queues, retry/recovery infrastructure, policy engine, telemetry/observability infrastructure.

### V9
Owns provider abstraction, prompts, summarization pipeline, token-aware chunking, hierarchical summarization, map-reduce, context strategies, streaming, quality-aware adaptive execution, resilience/fallback.

### V10
Owns bounded intelligence architecture, decision/evidence/experience/adaptation contracts, orchestration translation/guard/handoff, intelligence observability/explainability and certification.

### V11
Integrates and hardens these existing systems into one canonical product path.

Do not create a second summarization pipeline, a third provider abstraction, a parallel runtime, or a new intelligence subsystem.

## Locked V10 authority invariants

These invariants must remain true throughout V11 and V12:

- PRESERVE: no execution-change authority.
- ADVISORY: no execution-change authority.
- CONSTRAINED: bounded execution-change authority only.
- REVIEW: no execution-change authority; review required.
- Rejected directives cannot cross the orchestration handoff.
- Missing or insufficient historical evidence defaults toward PRESERVE.
- Invalid architecture state fails closed.
- Provenance must never be silently rewritten.
- Observability and explainability remain read-only.
- Provider/runtime implementation details remain outside core V10 intelligence contracts.
- Existing execution behavior remains the default unless bounded intelligence explicitly authorizes a constrained change.

Do not redesign V10 unless real V11 integration proves a genuine architecture defect.

## Current V11 architecture

M1 established the canonical application boundary:

```text
POST /api/v1/summarize
  -> app.routes.ai
  -> app.api.application.build_summarization_application()
  -> app.api.application.SummarizationApplication
```

`POST /summarize` remains a compatibility-only path and must not independently gain V11 product behavior.

M1 also established:
- application-level request/result contracts
- canonical/compatibility path inventory
- read-only execution metadata
- architecture guardrails

M2 integrated the canonical application with the existing V9 pipeline:

```text
SummarizationApplication
  -> AsyncSummarizationPipelineAdapter
  -> existing V9 SummarizationPipeline
  -> DIRECT / MAP_REDUCE / HIERARCHICAL
  -> existing async summarization service/provider path
```

M2 also established:
- async/sync pipeline bridge
- strategy execution through the canonical application
- aggregate provider token accounting across multi-call summarization
- canonical HTTP real-text integration with deterministic providers
- failure propagation without introducing premature resilience policy

V10 intelligence is NOT yet wired into the real canonical summarization execution flow. That is V11 M3.

## Immediate next phase

Start with:

### V11 M3 — V10 Intelligence Integration into Real Summarization Flow

Recommended increments:

- M3.1 — Application → V10 Intelligence Context / validated handoff boundary
- M3.2 — PRESERVE / ADVISORY / REVIEW application semantics
- M3.3 — CONSTRAINED execution translation
- M3.4 — real execution observation / feedback integration
- M3.5 — explainability and observability metadata integration
- M3.6 — M3 architecture certification and Git checkpoint

For M3.1, begin execution-neutral. Translate the real application context into existing V10 contracts and consume only a validated V10 handoff. Do not permit execution-changing behavior until the non-authoritative modes are proven.

## Remaining V11 roadmap

After M3:

- M4 — Frontend / API / Real-Text End-to-End Integration
- M5 — Streaming / Long-Document / Strategy Integration
- M6 — Provider Integration & Controlled Real-Provider Validation
- M7 — Resilience / Failure / Recovery Integration
- M8 — Performance & Reliability Hardening
- M9 — Product-Level End-to-End Certification
- M10 — Architecture Review / Release Closure / `v11.0.0`

Then begin V12 only from the frozen `v11.0.0` release baseline.

## V12 objective

V12 is feature-frozen production certification.

It should cover production-readiness certification, final documentation, release-candidate work, compatibility validation, deployment/runtime validation, final product checks, and final `v12.0.0`.

V12 is the project finish line.

## Development method

Proceed milestone by milestone:

design -> implementation -> focused tests -> affected subsystem tests -> full non-live regression -> pre-commit -> git diff check -> Git checkpoint

Do not jump ahead to later milestone functionality merely because it is convenient.

Prefer minimal integration changes over redesign.

## Validation gates

For every implementation increment, run focused tests first.

When V10 intelligence is affected:

```powershell
pytest app/tests/intelligence -q
```

Normal full regression:

```powershell
pytest -m "not live" -q
```

Repository hygiene:

```powershell
pre-commit run --all-files
git diff --check
git status
```

Live-provider tests remain explicitly marked `live` and must not run during ordinary development.

Do not spend provider API cost unless the milestone explicitly requires controlled live-provider validation.

## Latest validated baseline

At V11 M2 closure:

- full non-live regression: `3024 passed, 9 deselected`
- pre-commit: passed
- `git diff --check`: clear
- working tree: clean
- branch: `main`
- remote main: `627bb730157d9d42d2ff78abce13a9660dd6c14b`
- annotated tag `v11.0.0-m2^{}` resolves to the same commit

Treat unexpected regression from this baseline as something to investigate rather than normalize.

## Git discipline

Do not rewrite frozen tags or release commits.

Checkpoint pattern:

```powershell
git status
git diff --stat
git diff --check
pytest -m "not live" -q
pre-commit run --all-files
git diff --check
git add <explicit milestone files>
git diff --cached --stat
git diff --cached --check
git commit -m "feat(v11): <milestone description>"
git tag -a v11.0.0-mN -m "V11 MN - <milestone title>"
git push origin main
git push origin v11.0.0-mN
git status
git log -5 --oneline --decorate
git ls-remote origin refs/heads/main
git ls-remote --tags origin v11.0.0-mN
git ls-remote --tags origin "v11.0.0-mN^{}"
```

Use explicit staging. Do not commit local archives, credentials, `.env`, API keys, virtual environments, caches, or unrelated workspace artifacts.

## Project structure

Source code lives under `app/`.

Important areas:

- `app/api/` — application/API composition
- `app/routes/` — canonical public API routes
- `app/core/` — V11 integration contracts/adapters
- `app/summarization/` — V9 summarization-domain architecture
- `app/intelligence/` — V10 bounded intelligence
- `app/runtime/`, `app/orchestration/`, `app/distributed/` — V7/V8 execution/runtime
- `app/providers/`, `app/prompts/`, `app/services/` — canonical provider/prompt/service architecture
- `app/tests/` — project tests
- `docs/v10/` — frozen V10 release documentation
- `docs/v11/` — V11 architecture and milestone documentation

Avoid adding logic to `app/legacy/` unless explicitly fixing compatibility behavior.

## Coding conventions

- Python 3.11
- Black formatting
- Ruff linting
- explicit descriptive names
- deterministic behavior
- immutable contracts where architecture requires it
- fail closed at bounded-intelligence authority boundaries

## Security

Never commit secrets.

Use environment variables for provider credentials.

Keep normal tests deterministic and provider-free.

Do not expose provider/runtime details through V10 core intelligence contracts.

## Codex operating rule

Before implementing a milestone:
1. inspect the existing implementation and tests;
2. state the minimal integration plan;
3. preserve frozen architecture ownership;
4. implement incrementally;
5. run focused validation;
6. run full non-live regression before checkpoint;
7. report exact files changed and exact test results.

If existing architecture tests contradict a proposed change, investigate the repository contract first. Do not weaken architecture tests merely to make a change pass.

## Python environment — mandatory

This repository has an established and validated Python 3.11 virtual
environment:

`E:\Projects\ai-summarizer\venv311`

This environment is authoritative for local development and validation.

Do not use system Python installations such as:

`C:\Python314\python.exe`

Do not create another virtual environment.

Do not install project dependencies into system Python.

Do not upgrade, recreate, or modify `venv311` unless explicitly approved.

For deterministic agent execution, prefer invoking the virtual-environment
executables directly rather than relying on shell activation:

```powershell
.\venv311\Scripts\python.exe -m pytest <focused-test> -q
.\venv311\Scripts\python.exe -m pytest app/tests/intelligence -q
.\venv311\Scripts\python.exe -m pytest -m "not live" -q
.\venv311\Scripts\pre-commit.exe run --all-files
.\venv311\Scripts\python.exe -m black --check .
.\venv311\Scripts\python.exe -m ruff check .

## Pre-commit execution under Codex

Codex must use a repository-local pre-commit cache rather than the default
user-profile cache.

For every pre-commit command, set:

```powershell
$env:PRE_COMMIT_HOME = "$PWD\.cache\pre-commit"
.\venv311\Scripts\pre-commit.exe run --all-files