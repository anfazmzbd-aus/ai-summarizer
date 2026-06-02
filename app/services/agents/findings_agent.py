from tools import research_finding_tool
from app.services.registry.registry import (
    register_agent
)

@register_agent(
    "findings",
    depends_on=["summary"]
)
def findings_agent(state):

    state["findings"] = research_finding_tool(state["text"])

    return state