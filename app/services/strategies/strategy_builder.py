def build_strategy(intents):

    strategy = {"summary"}

    mapping = {

        "meeting_notes": {
            "actions"
        },

        "business_report": {
            "insights",
            "trend"
        },

        "research_report": {
            "findings"
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
        "trend"
    ]

    return [
        agent
        for agent in execution_order
        if agent in strategy
    ]
    #return list(strategy)