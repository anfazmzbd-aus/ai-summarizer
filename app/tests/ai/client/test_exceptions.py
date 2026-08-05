from app.ai import (
    LLMClientError,
    LLMTimeoutError,
)


def test_exception_types():

    assert issubclass(
        LLMTimeoutError,
        LLMClientError,
    )
