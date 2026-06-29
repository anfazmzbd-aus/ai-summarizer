from app.services.logging.logger import logger

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
            "sentiment",
            "risk",
            "root_cause",
            "forecast",
            "recommendation"
        },

        "research_report": {
            "findings",
            "sentiment",
            "risk",
            "recommendation"
        },

        "fallback": {
            "summary",
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

    logger.info(
        f"****STRATEGY (strategy builder): {strategy}"
    )

    preferred_order = [
        "summary",
        "actions",
        "insights",
        "findings",
        "trend",
        "sentiment",
        "risk",
        "root_cause",
        "recommendation"
    ]

    return sorted(
        strategy,
        key=lambda x: (
            preferred_order.index(x)
            if x in preferred_order
            else 999
        )
    )
