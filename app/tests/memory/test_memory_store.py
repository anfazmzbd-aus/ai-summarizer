from app.memory import (
    MemoryEntry,
    MemoryStore,
)


def test_store():

    store = MemoryStore()

    entry = MemoryEntry(
        key="k1",
        value="v1",
    )

    store.put(entry)

    assert store.get("k1") == entry

    assert store.keys() == ["k1"]

    store.delete("k1")

    assert store.get("k1") is None
