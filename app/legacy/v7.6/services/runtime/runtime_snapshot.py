from copy import deepcopy


class RuntimeSnapshot:

    @staticmethod
    def create(state):

        return {

            "execution_id":
                state.get(
                    "execution_id"
                ),

            "artifacts":
                deepcopy(
                    state.get(
                        "artifacts",
                        {}
                    )
                ),

            "context":
                deepcopy(
                    state.get(
                        "context",
                        {}
                    )
                ),

            "execution":
                deepcopy(
                    state.get(
                        "execution",
                        {}
                    )
                ),

            "plan":
                deepcopy(
                    state.get(
                        "plan",
                        {}
                    )
                )
        }