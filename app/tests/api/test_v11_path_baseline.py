"""V11 M1.3 externally reachable summarization-path baseline."""

from fastapi.routing import APIRoute

from app.main import app


def _post_paths() -> set[str]:
    paths: set[str] = set()

    for route in app.routes:
        if isinstance(route, APIRoute) and "POST" in route.methods:
            paths.add(route.path)

    return paths


def test_canonical_summarization_endpoint_is_registered() -> None:
    assert "/api/v1/summarize" in _post_paths()


def test_compatibility_summarization_endpoint_remains_registered() -> None:
    assert "/summarize" in _post_paths()


def test_canonical_and_compatibility_paths_are_distinct() -> None:
    paths = _post_paths()

    assert "/api/v1/summarize" in paths
    assert "/summarize" in paths
    assert "/api/v1/summarize" != "/summarize"
