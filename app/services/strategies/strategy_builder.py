def build_strategy(intents):

    strategy = {"summary"}

    mapping = {

        "meeting_notes": {
            "actions",
            "sentiment"
        },

        "business_report": {
            "insights",
            "trend",
            "sentiment"
        },

        "research_report": {
            "findings",
            "sentiment"
        }
    }

    for intent in intents:

        strategy.update(
            mapping.get(
                intent,
                set()
            )
        )
    execution_order = [
        "summary",
        "actions",
        "insights",
        "findings",
        "trend",
        "sentiment"
    ]
    print("STRATEGY:", strategy)
    return [
        agent
        for agent in execution_order
        if agent in strategy
    ]
    #return list(strategy)