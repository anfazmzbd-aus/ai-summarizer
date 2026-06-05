import re


def detect_risk(text):

    text = text.lower()

    if any(
        word in text
        for word in [
            "high risk",
            "great risk",
            "risky"
        ]
    ):
        return ["High Risk"]

    if any(
        word in text
        for word in [
            "low risk",
            "loless risky",
            "normal risk",
            "moderate risk"            
        ]
    ):
        return ["Low Risk"]

    return ["Moderate Risk"]