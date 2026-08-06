
coding standards
black
ruff
pytest
version policy
plugin development
testing expectations

# Contributing to AI Summarizer
## Coding Standards
Language: Python 3.11+
.
Typing: Mandatory strong typing with from __future__ import annotations
.
Models: Prefer dataclass(slots=True) for runtime objects to ensure immutability and performance
.
Tooling
Black: Automated formatting is mandatory. Run black . before every commit
.
Ruff: Static analysis and linting must pass with zero warnings
.
Pytest: All tests must pass. The current baseline is 458 passing tests
.
Version Policy
We follow Semantic Versioning
:
MAJOR: Architectural shifts or core runtime changes.
MINOR: New features, agents, or providers.
PATCH: Bug fixes and stabilization.
Plugin Development
New agents should be developed as plugins. Implement the BasePlugin interface and register your agent's capabilities in the PluginMetadata
.
Testing Expectations
Every feature must include a matching test file in app/tests/
.
Unit tests must use the MockProvider to remain deterministic
.
Integration tests must validate the full DAG execution pipeline
.