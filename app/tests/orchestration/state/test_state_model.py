from app.orchestration.state.state_model import State


def test_state_defaults_are_empty():
    state = State()

    assert state.global_context == {}
    assert state.artifacts == {}
    assert state.node_outputs == {}
    assert state.services == {}


def test_state_accepts_services():
    llm_service = object()

    state = State(
        global_context={"text": "hello"},
        services={
            "llm_service": llm_service,
        },
    )

    assert state.global_context["text"] == "hello"
    assert state.services["llm_service"] is llm_service


def test_services_are_separate_from_global_context():
    service = object()

    state = State(
        global_context={"text": "hello"},
        services={"llm_service": service},
    )

    assert "llm_service" not in state.global_context
    assert state.services["llm_service"] is service


def test_state_preserves_existing_artifacts_and_node_outputs():
    state = State(
        global_context={"text": "hello"},
        artifacts={"summary": "result"},
        node_outputs={"summary": {"summary": "result"}},
    )

    assert state.artifacts["summary"] == "result"
    assert state.node_outputs["summary"]["summary"] == "result"
