def clean_summary(text):

    headers = [
        "Meeting Notes",
        "Business Report",
        "Research Report"
    ]

    for header in headers:
        text = text.replace(
            header,
            ""
        )

    return text.strip()