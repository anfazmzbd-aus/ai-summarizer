from app.services.registry.registry import (
    register_agent
)

from app.services.tools.sentiment_tool import (
    detect_sentiment
)

@register_agent(
    "sentiment",
    depends_on=["summary"]
)
def sentiment_agent(state):

    sentiment = detect_sentiment(
        state["text"]
    )

    state["sentiment"] = sentiment

    state.setdefault(
        "artifacts",
        {}
    )["sentiment"] = sentiment

    return state