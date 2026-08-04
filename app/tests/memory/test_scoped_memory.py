from app.memory import (
    MemoryEntry,
    MemoryNamespace,
    ScopedMemory,
)


def test_scoped_memory():

    memory = ScopedMemory()

    memory.put(
        MemoryNamespace.GLOBAL,
        "default",
        MemoryEntry(
            key="k",
            value="v",
        ),
    )

    assert (
        memory.get(
            MemoryNamespace.GLOBAL,
            "default",
            "k",
        ).value
        == "v"
    )
