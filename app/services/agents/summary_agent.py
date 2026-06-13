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
    
    summary_length = state["summary_length"]

    input_words = len(text.split())
    input_tokens = len(text.split())
    print(
        f"**************INPUT WORDS: {input_words}**************"
    )
    print(
        f"**************INPUT TOKENS: {input_tokens}**************"
    )
    
    result = summarizer_model(
        text,

        max_new_tokens=min(
            50,
            input_tokens
        ),

        min_new_tokens=max(
            10,
            int(
                input_tokens * 0.6
            )
        ),

        do_sample=False,

        truncation=False
    )

    summary_text = result[0]["summary_text"]

    state["summary"] = postprocess_summary(
        summary_text
    )

    summary = (
        result[0]["summary_text"]
    )

    summary_sentences = {
        s.strip()
        for s in summary.split(".")
        if s.strip()
    }

    original_sentences = [
        s.strip()
        for s in text.split(".")
        if s.strip()
    ]

    preserve_keywords = [
        "revenue",
        "profit",
        "market",
        "risk",
        "research"
    ]

    for sentence in original_sentences:

        lower = sentence.lower()

        if (
            any(
                k in lower
                for k in preserve_keywords
            )
            and not any(
                sentence in x
                for x in summary_sentences
            )
        ):
            summary_sentences.add(
                sentence
            )

    ordered = []

    for sentence in original_sentences:

        if any(
            sentence in x
            for x in summary_sentences
        ):
            ordered.append(
                sentence
            )

    state["summary"] = (
        ". ".join(
            ordered
        ) + "."
    )

    input_count = max(
        1,
        len(raw_text.split())
    )

    state["summary_metrics"] = {

        "input_words":
            len(raw_text.split()),

        "summary_words":
            len(
                summary.split()
            ),

        "compression_ratio":
            round(
                len(
                    state["summary"].split()
                )
                /
                input_count,
                2
            )
    }

    logger.info(
        f"SUMMARY METRICS: "
        f"{state['summary_metrics']}"
    )
    return state