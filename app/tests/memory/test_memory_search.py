from app.memory import (
    IndexedEntry,
    MemoryIndex,
    MemoryNamespace,
    MemorySearch,
)


def create_index():

    index = MemoryIndex()

    index.add(
        IndexedEntry(
            key="1",
            namespace=MemoryNamespace.EXECUTION,
            scope="exec",
            value="customer summary report",
        )
    )

    index.add(
        IndexedEntry(
            key="2",
            namespace=MemoryNamespace.SESSION,
            scope="session",
            value="meeting notes",
        )
    )

    return index


def test_text_search():

    search = MemorySearch(create_index())

    result = search.search("summary")

    assert len(result) == 1


def test_namespace_search():

    search = MemorySearch(create_index())

    result = search.by_namespace(MemoryNamespace.SESSION)

    assert len(result) == 1
