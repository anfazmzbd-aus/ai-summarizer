from app.runtime.hooks.hook_context import HookContext


def test_hook_context():

    runtime_context = object()
    state = object()

    context = HookContext(
        runtime_context=runtime_context,
        state=state,
    )

    assert context.runtime_context is runtime_context
    assert context.state is state
