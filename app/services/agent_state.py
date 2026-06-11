from dataclasses import dataclass, field
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):

    text: str
    summary_length: str
    summary_metrics: dict
    selected_agents: list

    summary: str

    actions: list
    insights: list
    findings: list
    trends: list

    plan: dict
    metadata: dict

    artifacts: dict
