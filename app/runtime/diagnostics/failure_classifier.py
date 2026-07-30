from __future__ import annotations


class FailureClassifier:
    """
    Classifies runtime failures.
    """

    def classify(
        self,
        exception: Exception | None,
    ) -> str:

        if exception is None:
            return "none"

        name = type(exception).__name__

        if "Timeout" in name:
            return "timeout"

        if "Cancel" in name:
            return "cancellation"

        if "Validation" in name:
            return "validation_error"

        return "unknown"
