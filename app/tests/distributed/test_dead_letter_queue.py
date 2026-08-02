from app.distributed.protocols import TaskEnvelope
from app.distributed.recovery import DeadLetterQueue


def test_dead_letter_add():

    queue = DeadLetterQueue()

    queue.add(
        TaskEnvelope(
            task_id="1",
            execution_id="e",
            node_id="n",
            agent_type="summary",
        )
    )

    assert queue.size() == 1
