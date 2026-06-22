from app.services.graph.parallel_executor import execute_parallel
from app.services.runtime.retry_policy import RetryPolicy
from app.services.runtime.state_merger import merge_state
from app.services.logging.logger import logger


class DAGExecutor:

    def __init__(self):
        self.retry_policy = RetryPolicy()

    def execute_group(self, tasks, state):

        results = execute_parallel(tasks)

        failed = []
        success_state = state.copy()

        for r in results:

            if r.get("error"):

                failed.append(
                    r["agent"]
                )

            else:

                success_state.setdefault(
                    "artifacts",
                    {}
                )

                success_state[
                    "artifacts"
                ].update(
                    r.get(
                        "artifacts",
                        {}
                    )
                )

        return success_state, failed, results

    def retry_failed(self, group_tasks, state, failed_agents):

        retry_tasks = [
            task for task in group_tasks
            if task[0].__name__ == "run_agent"
            and task[1][0] in failed_agents
        ]

        if not retry_tasks:
            return state

        logger.info(
            f"****RETRYING NODES: {failed_agents}"
        )

        retry_results = execute_parallel(retry_tasks)

        retry_state = {
            "artifacts": {}
        }

        for r in retry_results:

            retry_state.setdefault(
                "artifacts",
                {}
            )

            retry_state[
                "artifacts"
            ].update(
                r.get(
                    "artifacts",
                    {}
                )
            )

        return merge_state(
            state,
            retry_state,
            overwrite_agents=failed_agents
        )