from app.runtime.persistence.execution_record import ExecutionRecord
from app.runtime.persistence.memory_backend import MemoryBackend
from app.runtime.persistence.persistence_manager import PersistenceManager


def make_record(execution_id):

    return ExecutionRecord(
        execution_id=execution_id,
        status="completed",
        outputs={},
    )


def test_manager_save():

    backend = MemoryBackend()

    manager = PersistenceManager(
        backend,
    )

    record = make_record("1")

    manager.save(record)

    assert manager.get("1") == record


def test_manager_delete():

    backend = MemoryBackend()

    manager = PersistenceManager(
        backend,
    )

    manager.save(make_record("1"))

    manager.delete("1")

    assert manager.get("1") is None


def test_manager_list():

    backend = MemoryBackend()

    manager = PersistenceManager(
        backend,
    )

    manager.save(make_record("1"))
    manager.save(make_record("2"))

    assert len(manager.list()) == 2
