class RuntimeMetrics:

    @staticmethod
    def collect(state):

        execution = (
            state.get(
                "execution",
                {}
            )
        )

        return {

            "execution_id":
                state.get(
                    "execution_id"
                ),

            "agent_count":
                execution.get(
                    "agent_count",
                    0
                ),

            "trace_count":
                execution.get(
                    "trace_count",
                    0
                ),

            "retry_count":
                execution.get(
                    "retry_count",
                    0
                ),

            "execution_time":
                execution.get(
                    "total_execution_time",
                    0
                )
        }