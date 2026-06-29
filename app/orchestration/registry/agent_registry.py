from app.orchestration.registry.agent_specs import (
    AgentSpec,
)

from app.orchestration.agents.summary import (
    SummaryAgent,
)

from app.orchestration.agents.insights import (
    InsightsAgent,
)

from app.orchestration.agents.actions import (
    ActionsAgent,
)

from app.orchestration.state.state_contracts import (
    DEFAULT_CONTRACT,
)


class AgentRegistry:

    def __init__(self):

        self._specs = {

            "summary":

            AgentSpec(
                name="summary",
                function_name="summary",
                agent=SummaryAgent(),
                contract=DEFAULT_CONTRACT,
                reads={"text"},
                writes={"summary"},
            ),

            "insights":

            AgentSpec(

                name="insights",

                function_name="insights",

                agent=InsightsAgent(),

                contract=DEFAULT_CONTRACT,

                dependencies=(
                    "summary",
                ),

                reads={
                    "summary"
                },

                writes={
                    "insight"
                },

            ),

            "actions":

            AgentSpec(

                name="actions",

                function_name="actions",

                agent=ActionsAgent(),

                contract=DEFAULT_CONTRACT,

                dependencies=(
                    "summary",
                ),

                reads={
                    "summary"
                },

                writes={
                    "actions"
                },

            ),

        }

    def get(
        self,
        name,
    ):
        return self._specs[
            name
        ]

    def resolve(
        self,
        function_name,
    ):

        for spec in self._specs.values():

            if (
                spec.function_name
                ==
                function_name
            ):

                return (
                    spec.agent
                )

        raise ValueError(
            function_name
        )

    def exists(
        self,
        name,
    ):
        return (
            name
            in self._specs
        )

    def list_agents(
        self,
    ):
        return list(
            self._specs.keys()
        )