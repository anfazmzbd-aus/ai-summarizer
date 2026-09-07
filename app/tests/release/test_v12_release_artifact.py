from scripts.build_release_artifact import should_include


def test_release_excludes_runtime_log():
    assert should_include("logs/agent_system.log") is False


def test_release_excludes_tests():
    assert should_include("app/tests/api/test_application.py") is False


def test_release_excludes_development_github_configuration():
    assert should_include(".github/workflows/ci.yml") is False


def test_release_excludes_v11_historical_documentation():
    assert should_include("docs/v11/ARCHITECTURE_INDEX.md") is False


def test_release_includes_application_source():
    assert should_include("app/main.py") is True


def test_release_includes_static_assets():
    assert should_include("static/app.js") is True


def test_release_includes_runtime_requirements():
    assert should_include("requirements.txt") is True


def test_release_includes_environment_example():
    assert should_include(".env.example") is True


def test_release_includes_v12_documentation():
    assert should_include("docs/v12/V12_GOVERNANCE.md") is True
