from app.services.agents import (
    summary_agent,
    actions_agent,
    insights_agent,
    findings_agent
)

AGENT_REGISTRY = {
    "summary": summary_agent,
    "actions": actions_agent,
    "insights": insights_agent,
    "findings": findings_agent,
}