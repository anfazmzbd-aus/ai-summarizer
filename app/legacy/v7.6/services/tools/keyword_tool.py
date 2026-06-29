import re


def extract_keywords(text):

    words = re.findall(
        r'\b[a-zA-Z]{5,}\b',
        text
    )

    return sorted(
        list(set(words))
    )