from app.orchestration.state.state_builder import StateBuilder


def test_build_creates_text_context():
    state = StateBuilder.build("hello world")

    assert state.global_context == {
        "text": "hello world",
    }


def test_build_initializes_empty_services():
    state = StateBuilder.build("hello world")

    assert state.services == {}


def test_build_accepts_runtime_services():
    llm_service = object()
    prompt_manager = object()

    state = StateBuilder.build(
        "hello world",
        services={
            "llm_service": llm_service,
            "prompt_manager": prompt_manager,
        },
    )

    assert state.services["llm_service"] is llm_service
    assert state.services["prompt_manager"] is prompt_manager


def test_build_copies_service_mapping():
    services = {
        "llm_service": object(),
    }

    state = StateBuilder.build(
        "hello world",
        services=services,
    )

    services["another_service"] = object()

    assert "another_service" not in state.services


def test_build_preserves_text_when_services_are_provided():
    llm_service = object()

    state = StateBuilder.build(
        "original text",
        services={
            "llm_service": llm_service,
        },
    )

    assert state.global_context["text"] == "original text"
    assert state.services["llm_service"] is llm_service
