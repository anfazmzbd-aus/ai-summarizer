from dataclasses import dataclass, field
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):

    text: str
    summary_length: str

    selected_agents: list

    summary: str

    artifacts: dict
    
    plan: dict
    metadata: dict