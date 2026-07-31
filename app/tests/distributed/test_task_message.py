from app.distributed.protocols import TaskEnvelope


def test_task_envelope_creation():

    task = TaskEnvelope(
        task_id="task-001",
        execution_id="exec-001",
        node_id="node-001",
        agent_type="summary",
    )

    assert task.task_id == "task-001"
    assert task.retry_count == 0


def test_task_retry_increment():

    task = TaskEnvelope(
        task_id="task-001",
        execution_id="exec-001",
        node_id="node-001",
        agent_type="summary",
    )

    task.increment_retry()

    assert task.retry_count == 1
