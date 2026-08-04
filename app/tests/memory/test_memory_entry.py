from app.memory import MemoryEntry


def test_memory_entry():

    entry = MemoryEntry(
        key="summary",
        value="example",
    )

    assert entry.key == "summary"
    assert entry.value == "example"
    assert entry.metadata == {}
