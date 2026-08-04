from app.plugins import CapabilityInfo


def test_capability_info():

    info = CapabilityInfo(
        name="summary",
        version="1.0",
        plugin="demo",
    )

    assert info.name == "summary"
    assert info.plugin == "demo"
