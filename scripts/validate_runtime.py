# scripts/validate_runtime.py


def validate():
    import app  # noqa: F401

    assert app is not None


if __name__ == "__main__":
    validate()
    print("Runtime validation passed")
