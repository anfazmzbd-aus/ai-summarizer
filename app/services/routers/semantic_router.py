def semantic_router(text):

    text = text.lower()

    scores = {
        "actions": 0,
        "insights": 0,
        "findings": 0
    }

    # actions
    for word in [
        "should",
        "must",
        "follow up",
        "need to"
    ]:
        if word in text:
            scores["actions"] += 1

    # business
    for word in [
        "revenue",
        "profit",
        "market",
        "sales"
    ]:
        if word in text:
            scores["insights"] += 1

    # research
    for word in [
        "research",
        "study",
        "analysis"
    ]:
        if word in text:
            scores["findings"] += 1

    selected = ["summary"]

    for agent, score in scores.items():

        if score > 0:
            selected.append(agent)

    return {
        "selected_agents": selected,
        "scores": scores
    }