from app.services.logging.logger import logger
import re

def extract_actions(text):

    keywords = [
        "should",
        "must",
        "need to",
        "needs to",
        "follow up"
    ]

    actions = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lower = line.lower()
        print("LINE:", repr(line))
        print("LOWER:", repr(lower))
        matched = [
            keyword
            for keyword in keywords
            if keyword in lower
        ]

        print("MATCHED KEYWORDS:", matched)
        
        matched = []

        for keyword in keywords:

            pattern = (
                r"\b"
                + re.escape(keyword)
                + r"\b"
            )

            if re.search(
                pattern,
                lower
            ):
                matched.append(
                    keyword
                )

        print(
            "MATCHED KEYWORDS:",
            matched
        )

        if matched:

            line = re.sub(
                r"^[A-Za-z\s]+:\s*",
                "",
                line
            )
            print(
                "ACTION MATCH:",
                line
            )
            actions.append(
                line.strip()
            )

    logger.info(f"****ACTION TOOL: {actions}")
    return list(
        dict.fromkeys(actions)
    )