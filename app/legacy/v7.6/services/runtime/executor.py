from app.services.graph.parallel_executor import execute_parallel
from app.services.runtime.retry_policy import RetryPolicy
from app.services.runtime.state_merger import merge_state
from app.services.logging.logger import logger
from copy import deepcopy

class DAGExecutor:

    def __init__(self):
        self.retry_policy = RetryPolicy()

    def execute_group(self, tasks, state):

        results = execute_parallel(tasks)

        failed = []
        success_state = deepcopy(state)
        success_state["artifacts"] = deepcopy(state.get("artifacts", {}))

        for r in results:

            if r.get("error"):

                failed.append(
                    r["agent"]
                )

            else:

                success_state.setdefault("artifacts",{})

                group_artifacts = {}
                group_artifacts.update(r.get("artifacts", {}))

                success_state["artifacts"].update(group_artifacts)

        return success_state, failed or [], results or []

    def retry_failed(self, group_tasks, state, failed_agents):

        retry_tasks = []

        for task in group_tasks:

            fn, args = task

            agent_name = args[0]
            agent_func = args[1]

            if agent_name in failed_agents:

                retry_tasks.append(
                    (
                        fn,
                        (
                            agent_name,
                            agent_func,
                            deepcopy(state)
                        )
                    )
                )

        if not retry_tasks:
            return state

        logger.info(
            f"****RETRYING NODES: {failed_agents}"
        )
        
        #retry_base_state = deepcopy(state)
        #retry_base_state["artifacts"] = deepcopy(state.get("artifacts", {}))

        from copy import deepcopy

        retry_input = deepcopy(
            state
        )

        retry_results = execute_parallel(
            [
                (
                    t[0],
                    (
                        t[1][0],
                        t[1][1],
                        retry_input
                    )
                )
                for t in retry_tasks
            ]
        )

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
            
        state[
            "execution"
        ][
            "retry_count"
        ] += 1

        state[
            "execution"
        ][
            "failed_agents"
        ] = failed_agents

        return merge_state(
            state,
            retry_state,
            overwrite_agents=failed_agents
        )