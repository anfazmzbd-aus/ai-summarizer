"""
Pytest configuration for the AI Summarizer test suite.
"""

from __future__ import annotations

import os

import pytest

from app.tests.fixtures.mock_llm import MockLLMProvider


@pytest.fixture
def mock_llm_provider() -> MockLLMProvider:
    """Return a deterministic mock LLM provider."""
    return MockLLMProvider()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register test-suite command-line options."""
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run tests marked as live.",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """
    Skip live tests unless explicitly enabled.
    """
    run_live = config.getoption("--run-live") or (
        os.getenv("RUN_LIVE_TESTS", "").strip().lower() in {"1", "true", "yes", "on"}
    )

    if run_live:
        return

    skip_live = pytest.mark.skip(
        reason=("live test skipped; use --run-live or " "RUN_LIVE_TESTS=1 to enable")
    )

    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
