from app.plugins import CompatibilityChecker


def test_compatible():

    checker = CompatibilityChecker()

    assert checker.compatible(
        "8.0",
        "7.9",
    )


def test_incompatible():

    checker = CompatibilityChecker()

    assert not checker.compatible(
        "7.8",
        "8.0",
    )
