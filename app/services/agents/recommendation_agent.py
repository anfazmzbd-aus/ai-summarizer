from app.services.registry.registry import (
    register_agent
)

from app.services.tools.recommendation_tool import (
    recommendation_tool
)

@register_agent(
    "recommendation",
    depends_on=["summary"]
)
def recommendation_agent(state):
    recommendations = recommendation_tool(state["text"])

    state.setdefault(
        "artifacts",
        {}
    )["recommendations"] = recommendations

    return state

