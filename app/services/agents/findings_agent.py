from tools import research_finding_tool

def findings_agent(state):

    state["findings"] = research_finding_tool(state["text"])

    return state