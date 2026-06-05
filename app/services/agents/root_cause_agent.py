from app.services.registry.registry import (
    register_agent
)

from app.services.tools.root_cause_tool import (
    root_cause_tool
)

@register_agent(
    "root_cause",
    depends_on=["summary"]
)
def root_cause_agent(state):

    state["artifacts"][
        "root_cause"
    ] = root_cause_tool(
        state["text"]
    )

    return state