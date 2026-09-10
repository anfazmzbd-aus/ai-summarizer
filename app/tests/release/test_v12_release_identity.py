from app.version import __version__


def test_v12_final_release_version_identity():
    assert __version__ == "12.0.0"
