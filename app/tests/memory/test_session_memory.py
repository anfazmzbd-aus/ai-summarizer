from app.memory import (
    MemoryEntry,
    ScopedMemory,
    SessionMemory,
)


def test_session_memory():

    memory = SessionMemory(
        ScopedMemory(),
        "session-1",
    )

    memory.put(
        MemoryEntry(
            key="language",
            value="en",
        )
    )

    assert memory.get("language").value == "en"
