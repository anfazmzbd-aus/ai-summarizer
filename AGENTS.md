# Repository Guidelines

## Project Structure & Module Organization
Source code lives under `app/`. Core runtime and orchestration logic is split across `app/runtime/`, `app/orchestration/`, `app/providers/`, `app/prompts/`, and `app/api/`. Tests live in `app/tests/`, with unit-style coverage grouped by feature area and higher-level checks in `app/tests/integration/` and `app/tests/api_contracts/`. Supporting assets and references live in `docs/`, `architecture/`, `static/`, and `scripts/`.

## Build, Test, and Development Commands
- `make test` or `pytest`: runs the full test suite under `app/tests/`.
- `make api` or `uvicorn app.main:app --reload`: starts the local API server with reload enabled.
- `make lint` or `ruff check .`: checks style and import issues.
- `make format` or `black .`: formats Python files to the repo standard.
- `python scripts/validate_runtime.py`: runs the runtime validation script used by the project.

## Coding Style & Naming Conventions
Use Python 3.11, 4-space indentation, and Black formatting with an 88-character line length. Keep imports sorted with `isort`/Black conventions, and prefer explicit, descriptive names for modules, classes, and functions. Follow existing package naming patterns such as `runtime_manager.py`, `summary_agent`, and `test_*.py`. Avoid adding logic to `app/legacy/` unless you are fixing legacy-specific behavior.

## Testing Guidelines
Pytest is the test runner. Mark live-provider tests with `live` and integration-dependent tests with `integration`; these are defined in `pyproject.toml`. Place new tests next to the feature area they cover, and name files `test_<feature>.py`. Prefer deterministic tests and use mocked providers for offline coverage when possible. If a change affects API behavior, add or update tests in `app/tests/api/` or `app/tests/api_contracts/`.

## Commit & Pull Request Guidelines
Git history favors short, imperative commits with optional scope or release tags, such as `feat(v9.3): ...` or `fix(deps): ...`. Keep PRs focused, describe the behavioral change, link related issues, and include screenshots or sample payloads when API responses change. Note any contract, prompt, or runtime implications explicitly.

## Security & Configuration Tips
Do not commit secrets. Use `.env.example` as the template for local configuration, and keep provider credentials and API keys in local environment variables only. When adding new providers or runtime integrations, verify both offline and live paths before merging.
