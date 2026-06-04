def semantic_router(
    text,
    intent_info,
    strategy
):

    text = text.lower()

    scores = {
        "actions": 0,
        "insights": 0,
        "findings": 0
    }

    reasons = {
        "actions": [],
        "insights": [],
        "findings": [],
        "trends": []
    }

    action_keywords = [
        "should",
        "must",
        "follow up",
        "need to"
    ]

    insight_keywords = [
        "revenue",
        "profit",
        "market",
        "sales"
    ]

    finding_keywords = [
        "research",
        "study",
        "analysis"
    ]

    for word in action_keywords:
        if word in text:
            scores["actions"] += 1
            reasons["actions"].append(
                f"{word} detected"
            )

    for word in insight_keywords:
        if word in text:
            scores["insights"] += 1
            reasons["insights"].append(
                f"{word} detected"
            )

    for word in finding_keywords:
        if word in text:
            scores["findings"] += 1
            reasons["findings"].append(
                f"{word} detected"
            )
    

    confidence = {}

    confidence["actions"] = round(
        scores["actions"] / len(action_keywords),
        2
    )

    confidence["insights"] = round(
        scores["insights"] / len(insight_keywords),
        2
    )

    confidence["findings"] = round(
        scores["findings"] / len(finding_keywords),
        2
    )

    if scores["actions"] > 0:
        selected_agents.append(
            "actions"
        )

    if scores["findings"] > 0:
        selected_agents.append(
            "findings"
        )  
    print("semantic_router")
    print(f"primary_intent: {intent_info['primary_intent']}")
    print(f"intents: {intent_info['intents']}")
    print(f"selected_agents: {strategy}")
    print(f"scores: {scores}")
    print(f"confidence: {confidence}")
    print(f"reasons: {reasons}")

    return {
        "primary_intent": intent_info["primary_intent"],
        "intents": intent_info["intents"],
        "selected_agents": strategy,
        "scores": scores,
        "confidence": confidence,
        "reasons": reasons
    }