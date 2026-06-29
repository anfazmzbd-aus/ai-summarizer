class GraphExporter:

    @staticmethod
    def export(state):

        plan = (
            state.get(
                "plan",
                {}
            )
        )

        groups = (
            plan.get(
                "parallel_groups",
                []
            )
        )

        nodes = []

        for group in groups:

            for agent in group:

                nodes.append({

                    "id":
                        agent,

                    "status":
                        "executed"
                })

        return {

            "nodes":
                nodes,

            "groups":
                groups
        }