from app.memory import (
    IndexedEntry,
    MemoryNamespace,
)


def test_indexed_entry():

    entry = IndexedEntry(
        key="summary",
        namespace=MemoryNamespace.EXECUTION,
        scope="exec-1",
        value="AI report",
    )

    assert entry.key == "summary"
    assert entry.namespace is MemoryNamespace.EXECUTION
