from app.services.registry.registry import (
    register_agent
)

from app.models.summarizer_model import (
    summarizer_model
)

from app.services.logging.logger import (
    logger
)


@register_agent(
    "summary"
)
def summary_agent(state):

    sections = state.get(
        "sections",
        {}
    )

    if sections:

        priority = [

            "business_report",

            "research_report",

            "meeting_notes",

            "general"
        ]

        blocks = []

        for name in priority:

            if sections.get(
                name
            ):

                blocks.append(
                    sections[
                        name
                    ]
                )

        summary_input = "\n".join(
            blocks
        )

    else:

        summary_input = state[
            "text"
        ]

    logger.info(
        f"SUMMARY INPUT:\n"
        f"{summary_input}"
    )

    word_count = len(
        summary_input.split()
    )

    logger.info(
        f"SUMMARY WORDS: "
        f"{word_count}"
    )

    # Structured summaries:
    # preserve order instead of model rewriting

    if word_count <= 30:

        state["summary"] = (
            summary_input
        )

    else:

        result = (
            summarizer_model(

                summary_input,

                max_length=min(
                    60,
                    int(
                        word_count * 0.7
                    )
                ),

                min_length=max(
                    8,
                    int(
                        word_count * 0.3
                    )
                ),

                do_sample=False
            )
        )

        state["summary"] = (
            result[0][
                "summary_text"
            ]
        )

    return state