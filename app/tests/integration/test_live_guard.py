"""
Live-test marker examples.

These tests are intentionally not part of the normal regression
execution path.
"""

import pytest


@pytest.mark.live
def test_live_execution_requires_explicit_opt_in():
    """
    Sentinel test proving that live tests are explicitly marked.

    The pytest collection hook controls whether this executes.
    """
    assert True
