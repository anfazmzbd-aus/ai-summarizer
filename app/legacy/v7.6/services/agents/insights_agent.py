from app.services.registry.registry import (
    register_agent
)
from app.services.tools.insight_tool import (
    business_insight_tool
)

@register_agent(
    "insights",
    depends_on=[], # depends_on["summary"] removed in V7.6 ph6
    produces=["insights"]
)
def insights_agent(state):
    insights = business_insight_tool(state["text"])
    state.setdefault(
        "artifacts",
        {}
    )["insights"] = insights

    return state

