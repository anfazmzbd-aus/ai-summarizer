import time

from app.runtime.cache.cache_policy import CachePolicy
from app.runtime.cache.execution_cache import ExecutionCache


def test_cache_put_get():

    cache = ExecutionCache()

    cache.put(
        "summary",
        {"summary": "hello"},
    )

    assert cache.get("summary") == {
        "summary": "hello",
    }


def test_cache_returns_none_for_missing_key():

    cache = ExecutionCache()

    assert cache.get("missing") is None


def test_cache_overwrites_existing_key():

    cache = ExecutionCache()

    cache.put("summary", 1)
    cache.put("summary", 2)

    assert cache.get("summary") == 2


def test_cache_delete():

    cache = ExecutionCache()

    cache.put("summary", 1)

    cache.delete("summary")

    assert cache.get("summary") is None


def test_cache_clear():

    cache = ExecutionCache()

    cache.put("a", 1)
    cache.put("b", 2)

    cache.clear()

    assert cache.get("a") is None
    assert cache.get("b") is None


def test_cache_contains():

    cache = ExecutionCache()

    cache.put("summary", 1)

    assert "summary" in cache
    assert "missing" not in cache


def test_cache_ttl_expiration():

    cache = ExecutionCache(
        CachePolicy(
            ttl_seconds=1,
        )
    )

    cache.put("x", 123)

    time.sleep(1.1)

    assert cache.get("x") is None


def test_cache_respects_max_entries():

    cache = ExecutionCache(
        CachePolicy(
            max_entries=2,
        )
    )

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    assert len(cache) <= 2
