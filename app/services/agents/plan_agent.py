def plan_agent(state):

    text = state["text"].lower()

    selected = ["summary"]  # always run summary

    # -------------------------
    # ACTIONS SIGNALS
    # -------------------------
    if any(word in text for word in [
        "meeting",
        "agenda",
        "follow up",
        "action item",
        "should",
        "must",
        "need to"
    ]):
        selected.append("actions")

    # -------------------------
    # INSIGHTS SIGNALS
    # -------------------------
    if any(word in text for word in [
        "revenue",
        "profit",
        "sales",
        "market",
        "growth",
        "increase",
        "decrease"
    ]):
        selected.append("insights")

    # -------------------------
    # FINDINGS SIGNALS
    # -------------------------
    if any(word in text for word in [
        "research",
        "study",
        "analysis",
        "finding",
        "result",
        "report"
    ]):
        selected.append("findings")

    state["selected_agents"] = selected

    state["plan"] = {
        "selected_agents": selected
    }

    return state