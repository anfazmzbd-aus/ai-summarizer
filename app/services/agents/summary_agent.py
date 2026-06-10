from app.models.summarizer_model import summarizer_model
from app.services.registry.registry import (
    register_agent
)
from app.services.tools.summary_cleaner import (
    clean_summary
)

@register_agent("summary")

def summary_agent(state):

    text = state["text"]

    summary_length = state["summary_length"]

    input_words = len(text.split())

    if input_words < 40:

        state["summary"] = clean_summary(
            text
        )
        print(f"=== SUMMARY AGENT: Generated summary {state['summary']} words ===")
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

    summary_text = result[0]["summary_text"]

    state["summary"] = clean_summary(
        summary_text
    )

    print(f"=== SUMMARY AGENT: Generated summary {state['summary']} words ===")

    return state