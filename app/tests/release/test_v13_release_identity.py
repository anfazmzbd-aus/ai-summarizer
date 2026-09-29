from app.version import __version__


def test_v13_release_candidate_version_identity():
    assert __version__ == "13.0.0-rc1"
