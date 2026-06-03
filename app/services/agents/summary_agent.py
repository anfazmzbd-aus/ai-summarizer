from app.models.summarizer_model import summarizer_model
from app.services.registry.registry import (
    register_agent
)

@register_agent("summary")

def summary_agent(state):

    text = state["text"]

    summary_length = state["summary_length"]

    input_words = len(text.split())

    if input_words < 40:
        state["summary"] = text
        return state

    if summary_length == "short":
        max_len = min(80, max(40, input_words))
        min_len = 20

    elif summary_length == "medium":
        max_len = min(120, max(60, input_words))
        min_len = 30

    else:
        max_len = min(160, max(80, input_words))
        min_len = 40

    result = summarizer_model(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        truncation=True
    )

    state["summary"] = result[0]["summary_text"]

    return state