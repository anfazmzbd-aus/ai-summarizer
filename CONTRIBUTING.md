# Contributing Guide

## Workflow
Create a feature branch before making changes, using a name like `feature/<topic>` or `fix/<topic>`. Do not commit directly to `main`. Keep changes focused on one behavior or layer at a time.

## Local Checks
- `pytest`: run the full test suite under `app/tests/`.
- `ruff check .`: catch style and import issues.
- `black .`: format Python files to repo standards.
- `uvicorn app.main:app --reload`: verify the API starts locally when relevant.

## Architecture Rules
Preserve the repo’s deterministic, contract-driven design. Prefer extending existing `ExecutionGraph`, runtime, provider, or prompt abstractions instead of introducing ad hoc runtime paths. Keep state immutable during execution and validate contracts before committing results back to shared state.

## Testing Expectations
Add or update tests with the change, especially for API behavior, provider integration, and runtime orchestration. Keep tests deterministic by default and use mocked providers for offline coverage when possible. Mark live-provider tests with `live` and integration-dependent tests with `integration`.

## Pull Requests
Include a short description of the change, any related issue links, and notes on contract, prompt, or runtime impact. Update documentation when behavior changes. If the API output changes, include sample requests or screenshots where useful.
