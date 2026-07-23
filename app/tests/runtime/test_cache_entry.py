from app.runtime.cache.cache_entry import CacheEntry


def test_cache_entry_fields():

    entry = CacheEntry(
        key="abc",
        value={"summary": "done"},
        created_at=123.4,
    )

    assert entry.key == "abc"
    assert entry.value["summary"] == "done"
    assert entry.created_at == 123.4


def test_cache_entry_equality():

    a = CacheEntry(
        key="k",
        value=1,
        created_at=10,
    )

    b = CacheEntry(
        key="k",
        value=1,
        created_at=10,
    )

    assert a == b
