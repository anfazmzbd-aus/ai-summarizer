"""
AI Summarizer V8.0

Remote executor factory.
"""

from __future__ import annotations

from .executor_interface import RemoteExecutor
from .grpc_executor import GRPCExecutor
from .http_executor import HTTPExecutor
from .local_executor import LocalExecutor


class AdapterFactory:
    """
    Creates execution adapters.
    """

    @staticmethod
    def create(
        adapter: str,
        **kwargs,
    ) -> RemoteExecutor:

        if adapter == "local":

            return LocalExecutor(kwargs["execution_engine"])

        if adapter == "http":

            return HTTPExecutor(
                endpoint=kwargs["endpoint"],
                timeout=kwargs.get(
                    "timeout",
                    30.0,
                ),
            )

        if adapter == "grpc":

            return GRPCExecutor(client=kwargs["client"])

        raise ValueError(f"Unsupported adapter: {adapter}")
