import re


def preprocess_summary_input(text):

    lines = []

    ignore_headers = {
        "Meeting Notes",
        "Business Report",
        "Research Report"
    }

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line in ignore_headers:
            continue

        lines.append(line)

    return " ".join(lines)