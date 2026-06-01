def plan_agent(state):

    text = state["text"].lower()

    selected = ["summary"]  # always run summary

    business_signals = [
        "revenue",
        "profit",
        "margin",
        "sales",
        "market",
        "growth",
        "performance",
        "%"
    ]

    signal_count = sum(
        1 for w in business_signals if w in text
    )

    is_business = signal_count > 0
    is_strong_business = signal_count >= 3

    if is_business:
        selected.append("insights")

    if "meeting" in text or "should" in text or "must" in text:
        selected.append("actions")

    if "research" in text or "study" in text:
        selected.append("findings")

    # 🔥 NEW RULE: full KPI report
    if is_strong_business:
        selected = ["summary", "insights"]

    state["selected_agents"] = selected

    state["plan"] = {
        "selected_agents": selected
    }
    print("PLAN Selected Agents:", state["selected_agents"])
    print("PLAN State:", state["plan"])
    return state

"""
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
    business_keywords = [
        "revenue",
        "profit",
        "margin",
        "sales",
        "market",
        "growth",
        "increase",
        "decrease",
        "expanded",
        "performance",
        "%"
    ]

    is_business = any(
        word in text for word in business_keywords
    )
    # If business data exists, treat as implicit analysis context
    if is_business:
        if "actions" not in selected:
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
"""