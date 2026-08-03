"""
OpenTelemetry provider setup.
"""

from __future__ import annotations

from opentelemetry import trace

from opentelemetry.sdk.trace import (
    TracerProvider,
)

from opentelemetry.sdk.trace.export import (
    # BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)

_provider = None


def configure_tracing(
    *,
    service_name: str = "ai-summarizer",
    console_export: bool = False,
) -> None:
    global _provider

    if _provider is not None:
        return

    provider = TracerProvider()

    if console_export:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    _provider = provider


def shutdown_tracing() -> None:
    global _provider

    if _provider is not None:
        _provider.shutdown()
        _provider = None


def get_tracer(
    name: str = "ai-summarizer",
):

    return trace.get_tracer(name)
