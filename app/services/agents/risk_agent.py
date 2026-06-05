import re
from app.services.registry.registry import (
    register_agent
)
from app.services.tools.risk_tool import (
    detect_risk
)

@register_agent(
    "risk",
    depends_on=["summary"]
)
def risk_agent(state):

    risk = detect_risk(
        state["text"]
    )

    state.setdefault(
        "artifacts",
        {}
    )["risk"] = risk

    return state