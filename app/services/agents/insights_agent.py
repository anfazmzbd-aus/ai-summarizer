from tools import business_insight_tool

def insights_agent(state):

    state["insights"] = business_insight_tool(state["text"])

    return state

