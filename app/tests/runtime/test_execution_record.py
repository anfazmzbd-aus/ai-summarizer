from app.runtime.persistence.execution_record import ExecutionRecord


def test_execution_record_creation():

    record = ExecutionRecord(
        execution_id="exec-1",
        status="completed",
        outputs={
            "summary": "hello",
        },
    )

    assert record.execution_id == "exec-1"
    assert record.status == "completed"
    assert record.outputs["summary"] == "hello"


def test_execution_record_defaults():

    record = ExecutionRecord(
        execution_id="1",
        status="running",
    )

    assert record.outputs == {}
    assert record.metadata == {}
