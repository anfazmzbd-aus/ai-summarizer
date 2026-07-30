from app.runtime.diagnostics.failure_classifier import (
    FailureClassifier,
)


class CustomTimeoutError(Exception):
    pass


class CustomValidationError(Exception):
    pass


def test_no_exception():

    classifier = FailureClassifier()

    result = classifier.classify(
        None,
    )

    assert result == "none"


def test_timeout_classification():

    classifier = FailureClassifier()

    result = classifier.classify(
        CustomTimeoutError(),
    )

    assert result == "timeout"


def test_validation_classification():

    classifier = FailureClassifier()

    result = classifier.classify(
        CustomValidationError(),
    )

    assert result == "validation_error"


def test_unknown_classification():

    classifier = FailureClassifier()

    result = classifier.classify(
        RuntimeError(),
    )

    assert result == "unknown"
