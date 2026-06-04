import re


def extract_actions(text):

    sentences = re.split(
        r'[.!?]\s+',
        text
    )

    keywords = [
        "should",
        "must",
        "need to",
        "needs to",
        "follow up",
        "action",
        "task"
    ]

    actions = []

    for s in sentences:

        s = s.strip()
        lower = s.lower()

        if (
            "should" in lower
            or "must" in lower
            or "need to" in lower
            or "needs to" in lower
        ):
            s = re.sub(
                r"^[A-Za-z\s]+:\s*",
                "",
                s
            )

            actions.append(s.strip())

    return list(dict.fromkeys(actions))