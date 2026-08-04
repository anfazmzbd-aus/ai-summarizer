from app.memory import (
    IndexedEntry,
    MemoryIndex,
    MemoryNamespace,
)


def test_index():

    index = MemoryIndex()

    index.add(
        IndexedEntry(
            key="1",
            namespace=MemoryNamespace.GLOBAL,
            scope="default",
            value="hello",
        )
    )

    assert index.count() == 1

    assert len(index.all()) == 1
