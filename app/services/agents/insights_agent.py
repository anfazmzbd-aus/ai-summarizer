from tools import business_insight_tool
from app.services.registry.registry import (
    register_agent
)
from app.services.tools.insight_tool import (
    business_insight_tool
)

@register_agent(
    "insights",
    depends_on=["summary"]
)
def insights_agent(state):

    state["insights"] = business_insight_tool(state["text"])

    return state

