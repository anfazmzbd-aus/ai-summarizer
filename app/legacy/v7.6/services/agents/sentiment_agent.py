from app.services.registry.registry import (
    register_agent
)

from app.services.tools.sentiment_tool import (
    detect_sentiment
)

@register_agent(
    "sentiment",
    depends_on=[] # depends_on["summary"] removed in V7.6 ph6
)
def sentiment_agent(state):

    sentiment = detect_sentiment(
        state["text"]
    )

    state.setdefault(
        "artifacts",
        {}
    )["sentiment"] = sentiment

    return state