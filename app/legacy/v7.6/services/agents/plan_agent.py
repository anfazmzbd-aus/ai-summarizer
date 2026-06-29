from app.services.registry.registry import (
    register_agent
)

@register_agent("plan")
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

    return state
