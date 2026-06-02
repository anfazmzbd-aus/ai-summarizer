def semantic_router(text):

    text = text.lower()

    scores = {
        "actions": 0,
        "insights": 0,
        "findings": 0
    }

    reasons = {
        "actions": [],
        "insights": [],
        "findings": []
    }

    # Actions
    action_keywords = [
        "should",
        "must",
        "follow up",
        "need to"
    ]

    for word in action_keywords:
        if word in text:
            scores["actions"] += 1
            reasons["actions"].append(
                f"{word} detected"
            )

    # Insights
    insight_keywords = [
        "revenue",
        "profit",
        "market",
        "sales"
    ]

    for word in insight_keywords:
        if word in text:
            scores["insights"] += 1
            reasons["insights"].append(
                f"{word} detected"
            )

    # Findings
    finding_keywords = [
        "research",
        "study",
        "analysis"
    ]

    for word in finding_keywords:
        if word in text:
            scores["findings"] += 1
            reasons["findings"].append(
                f"{word} detected"
            )

    selected = ["summary"]

    for agent, score in scores.items():
        if score > 0:
            selected.append(agent)

    confidence = {}

    for agent, score in scores.items():

        max_score = {
            "actions": len(action_keywords),
            "insights": len(insight_keywords),
            "findings": len(finding_keywords)
        }[agent]

        confidence[agent] = round(
            score / max_score,
            2
        )

    return {
        "selected_agents": selected,
        "scores": scores,
        "confidence": confidence,
        "reasons": reasons
    }