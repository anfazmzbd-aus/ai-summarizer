from app.observability.tracing import (
    configure_tracing,
    get_tracer,
)


def test_provider_configuration():

    configure_tracing(console_export=False)

    tracer = get_tracer()

    assert tracer is not None
