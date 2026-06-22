from copy import deepcopy


def build_execution_context(
    state
):

    return {

        "context": {

            "text":
                state["text"],

            "summary_length":
                state["summary_length"],

            "selected_agents":
                deepcopy(
                    state.get(
                        "selected_agents",
                        []
                    )
                )
        },

        "state":
            deepcopy(
                state
            ),

        "runtime": {

            "timings": {},

            "executed": []
        },

        "artifacts": deepcopy(
            state.get(
                "artifacts",
                {}
            )
        )
    }