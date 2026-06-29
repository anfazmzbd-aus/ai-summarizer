import re
from app.services.registry.registry import (
    register_agent
)
from app.services.tools.risk_tool import (
    detect_risk
)

@register_agent(
    "risk",
    depends_on=["insights", "findings"],
    produces=["risk"]
)

def risk_agent(state):

    insights = (
        state.get(
            "artifacts",
            {}
        ).get(
            "insights",
            []
        )
    )

    findings = (
        state.get(
            "artifacts",
            {}
        ).get(
            "findings",
            []
        )
    )

    risk = detect_risk(
        insights,
        findings
    )

    state.setdefault(
        "artifacts",
        {}
    )["risk"] = risk

    return state