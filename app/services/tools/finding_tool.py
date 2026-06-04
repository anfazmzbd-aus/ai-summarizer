def research_finding_tool(text):

    findings = []

    sentences = re.split(
        r"[.!?]\s+",
        text
    )

    keywords = [
        "research",
        "study",
        "analysis",
        "result"
    ]

    for sentence in sentences:

        if any(
            keyword in sentence.lower()
            for keyword in keywords
        ):
            findings.append(
                sentence.strip()
            )

    return list(dict.fromkeys(findings))