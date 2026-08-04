from app.memory import (
    ExecutionMemory,
    MemoryEntry,
    ScopedMemory,
)


def test_execution_memory():

    memory = ExecutionMemory(
        ScopedMemory(),
        "exec-1",
    )

    memory.put(
        MemoryEntry(
            key="summary",
            value="done",
        )
    )

    assert memory.get("summary").value == "done"
