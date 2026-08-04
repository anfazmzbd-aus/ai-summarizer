from app.memory import (
    MemoryEntry,
    MemoryStore,
)


def test_memory_interface():

    memory = MemoryStore()

    memory.put(
        MemoryEntry(
            key="x",
            value=123,
        )
    )

    assert memory.get("x").value == 123
