from .agent_state import AgentState


def router_node(state: AgentState):

    text = state["text"].lower()

    selected = ["summary"]

    if any(word in text for word in [
        "action",
        "task",
        "todo",
        "next step"
    ]):
        selected.append("actions")

    if any(word in text for word in [
        "analysis",
        "insight",
        "trend",
        "reason"
    ]):
        selected.append("insights")

    if any(word in text for word in [
        "problem",
        "issue",
        "finding"
    ]):
        selected.append("findings")

    if any(word in text for word in [
        "plan",
        "strategy",
        "roadmap"
    ]):
        selected.append("plan")

    state["selected_agents"] = selected

    return state