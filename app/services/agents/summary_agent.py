from app.models.summarizer_model import summarizer_model
from app.services.tools.summary_preprocessor import (
    preprocess_summary_input
)
from app.services.tools.summary_postprocessor import (
    postprocess_summary
)
from app.services.registry.registry import (
    register_agent
)
from app.services.logging.logger import logger

@register_agent("summary")

def summary_agent(state):

    raw_text = state["text"]

    text = preprocess_summary_input(
        raw_text
    )
    print(
        "PREPROCESSED SUMMARY INPUT:"
    )
    print(text)
    summary_length = state["summary_length"]

    input_words = len(text.split())
    input_tokens = len(text.split())
    print(
        f"**************INPUT WORDS: {input_words}**************"
    )
    print(
        f"**************INPUT TOKENS: {input_tokens}**************"
    )
    
    if summary_length == "short":

        max_len = min(
            max(10, input_tokens - 2),
            40
        )

        min_len = max(
            5,
            max_len // 2
        )

    elif summary_length == "medium":

        max_len = min(
            max(20, input_tokens),
            80
        )

        min_len = max(
            10,
            max_len // 2
        )

    else:

        max_len = min(
            max(30, input_tokens),
            120
        )

        min_len = max(
            15,
            max_len // 2
        )

    max_len = min(
        max_len,
        input_words
    )

    min_len = min(
        min_len,
        max_len - 1
    )

    if not text.strip():

        state["summary"] = (
            "No summary content available."
        )

        state["summary_metrics"] = {
            "input_words": 0,
            "summary_words": 0,
            "compression_ratio": 0
        }

        return state

    input_tokens = max(
        1,
        len(text.split())
    )

    max_len = min(
        max_len,
        input_tokens
    )

    min_len = min(
        min_len,
        max_len - 1
    )

    result = summarizer_model(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        truncation=True
    )

    summary_text = result[0]["summary_text"]

    state["summary"] = postprocess_summary(
        summary_text
    )

    state["summary_metrics"] = {

        "input_words":
            len(raw_text.split()),

        "summary_words":
            len(
                state["summary"].split()
            ),

        "compression_ratio":
            round(
                len(
                    state["summary"].split()
                )
                /
                len(
                    raw_text.split()
                ),
                2
            )
    }

    logger.info(
        f"SUMMARY METRICS: "
        f"{state['summary_metrics']}"
    )
    return state