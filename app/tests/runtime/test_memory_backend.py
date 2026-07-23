from app.runtime.persistence.execution_record import ExecutionRecord
from app.runtime.persistence.memory_backend import MemoryBackend


def make_record(execution_id):

    return ExecutionRecord(
        execution_id=execution_id,
        status="completed",
        outputs={},
    )


def test_save_record():

    backend = MemoryBackend()

    record = make_record("1")

    backend.save(record)

    assert backend.get("1") == record


def test_missing_record_returns_none():

    backend = MemoryBackend()

    assert backend.get("missing") is None


def test_delete_record():

    backend = MemoryBackend()

    backend.save(make_record("1"))

    backend.delete("1")

    assert backend.get("1") is None


def test_list_records():

    backend = MemoryBackend()

    backend.save(make_record("1"))
    backend.save(make_record("2"))

    records = backend.list()

    assert len(records) == 2
