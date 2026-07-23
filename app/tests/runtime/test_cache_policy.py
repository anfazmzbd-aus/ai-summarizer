from app.runtime.cache.cache_policy import CachePolicy


def test_default_cache_policy():

    policy = CachePolicy()

    assert policy.enabled is True
    assert policy.ttl_seconds > 0
    assert policy.max_entries > 0


def test_custom_cache_policy():

    policy = CachePolicy(
        enabled=False,
        ttl_seconds=30,
        max_entries=10,
    )

    assert policy.enabled is False
    assert policy.ttl_seconds == 30
    assert policy.max_entries == 10
