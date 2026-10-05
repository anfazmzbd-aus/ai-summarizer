from app.version import __version__


def test_v13_final_release_version_identity():
    assert __version__ == "13.0.0"
