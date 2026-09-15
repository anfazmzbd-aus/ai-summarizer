"""V13 M2.1 modern frontend structure contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_v13_frontend_exposes_product_shell() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")

    html = response.text

    assert 'class="app-shell"' in html
    assert 'class="app-header"' in html
    assert 'id="mainContent"' in html
    assert 'class="workspace"' in html
    assert 'class="app-footer"' in html


def test_v13_frontend_exposes_source_workspace() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    html = response.text

    assert 'id="summaryForm"' in html
    assert 'id="inputText"' in html
    assert 'id="summarizeButton"' in html
    assert 'id="status"' in html
    assert 'id="error"' in html


def test_v13_frontend_exposes_result_workspace() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    html = response.text

    assert 'id="resultEmpty"' in html
    assert 'id="result"' in html
    assert 'id="summaryText"' in html


def test_v13_frontend_preserves_supported_metadata_targets() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    html = response.text

    assert 'id="strategyValue"' in html
    assert 'id="chunkCountValue"' in html
    assert 'id="intelligenceModeValue"' in html
    assert 'id="observabilityStatusValue"' in html


def test_v13_frontend_preserves_canonical_api_path() -> None:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200

    javascript = response.text

    assert 'fetch("/api/v1/summarize"' in javascript
    assert 'fetch("/summarize"' not in javascript


def test_v13_frontend_hides_empty_state_after_success() -> None:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200

    javascript = response.text

    assert 'resultEmpty.classList.add("hidden");' in javascript
    assert 'result.classList.remove("hidden");' in javascript


def test_v13_frontend_has_accessible_status_regions() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    html = response.text

    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'role="alert"' in html
