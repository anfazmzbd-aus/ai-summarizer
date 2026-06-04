def detect_sentiment(text):

    text = text.lower()

    if any(
        word in text
        for word in [
            "improved",
            "growth",
            "increase",
            "success"
        ]
    ):
        return ["Positive"]

    if any(
        word in text
        for word in [
            "declined",
            "loss",
            "drop",
            "risk",
            "fell"
        ]
    ):
        return ["Negative"]

    return ["Neutral"]