from app.version import __version__


def test_v12_release_candidate_version_identity():
    assert __version__ == "12.0.0-rc1"
