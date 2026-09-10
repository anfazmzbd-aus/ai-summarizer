from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP_JS = ROOT / "static" / "app.js"


def test_v12_frontend_javascript_has_no_stray_release_identifier():
    javascript = APP_JS.read_text(encoding="utf-8")

    assert 'result.classList.remove("hidden");s' not in javascript
    assert 'result.classList.remove("hidden");' in javascript
