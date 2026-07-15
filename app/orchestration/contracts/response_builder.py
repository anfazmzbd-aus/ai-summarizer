import uuid

from app.orchestration.contracts.execution_response import (
    ExecutionResponse,
)


class ResponseBuilder:

    @staticmethod
    def build(
        state,
        trace=None,
        metrics=None,
        errors=None,
    ) -> ExecutionResponse:

        result = (
            state.artifacts
            if hasattr(
                state,
                "artifacts",
            )
            else {}
        )

        node_outputs = (
            state.node_outputs
            if hasattr(
                state,
                "node_outputs",
            )
            else {}
        )

        return ExecutionResponse(
            execution_id=str(uuid.uuid4()),
            status=("failed" if errors else "success"),
            result=result,
            node_outputs=node_outputs,
            trace=(trace.export() if trace else []),
            metrics=(metrics.export() if metrics else {}),
            errors=(errors or []),
            metadata={
                "version": "v7.7",
                "execution_model": "deterministic_dag",
            },
        )
