from app.runtime.checkpoint.checkpoint import Checkpoint


def test_checkpoint_creation():

    checkpoint = Checkpoint(
        execution_id="1",
        node="summary",
        state={
            "step": 1,
        },
    )

    assert checkpoint.execution_id == "1"
    assert checkpoint.node == "summary"
    assert checkpoint.state["step"] == 1


def test_checkpoint_has_timestamp():

    checkpoint = Checkpoint(
        execution_id="1",
        node="summary",
        state={},
    )

    assert checkpoint.created_at is not None
