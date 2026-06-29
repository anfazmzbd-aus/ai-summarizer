import re


HEADERS = {
    "business_report": [
        "business report"
    ],

    "meeting_notes": [
        "meeting notes"
    ],

    "research_report": [
        "research report"
    ]
}


def normalize_header(text):

    return (
        text
        .lower()
        .strip()
        .rstrip(":")
    )


def split_sections(text):

    sections = {}

    current = None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        normalized = normalize_header(
            line
        )

        matched = False

        for intent, markers in HEADERS.items():

            if normalized in markers:

                current = intent

                sections.setdefault(
                    current,
                    []
                )

                matched = True

                break

        if matched:
            continue

        if current is None:

            current = "general"

            sections.setdefault(
                current,
                []
            )

        sections[
            current
        ].append(
            line
        )

    return {

        key: "\n".join(
            value
        )

        for key, value
        in sections.items()

        if value
    }