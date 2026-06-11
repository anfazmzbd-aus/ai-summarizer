import re


def postprocess_summary(summary):

    summary = re.sub(
        r"\s+",
        " ",
        summary
    )

    return summary.strip()