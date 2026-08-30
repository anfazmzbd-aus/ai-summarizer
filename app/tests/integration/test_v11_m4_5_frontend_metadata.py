"""V11 M4.5 frontend metadata visibility contract."""

from fastapi.testclient import TestClient

from app.main import app


def test_frontend_exposes_execution_metadata_targets() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200

    html = response.text

    assert 'id="strategyValue"' in html
    assert 'id="chunkCountValue"' in html
    assert 'id="intelligenceModeValue"' in html
    assert 'id="observabilityStatusValue"' in html


def test_frontend_javascript_consumes_product_metadata() -> None:
    response = TestClient(app).get("/static/app.js")

    assert response.status_code == 200

    javascript = response.text

    assert "metadata.strategy" in javascript
    assert "metadata.chunk_count" in javascript
    assert "metadata.intelligence_mode" in javascript
    assert "metadata.observability_status" in javascript

    assert '"/api/v1/summarize"' in javascript
