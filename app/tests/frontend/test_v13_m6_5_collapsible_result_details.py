from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INDEX_HTML = ROOT / "app" / "templates" / "index.html"
APP_JS = ROOT / "static" / "app.js"


def read_index() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


def read_app_js() -> str:
    return APP_JS.read_text(encoding="utf-8")


def processing_details_markup() -> str:
    html = read_index()
    start = html.index('class="processing-details"')
    end = html.index("</section>", start)
    return html[start:end]


def test_processing_details_remains_present():
    html = read_index()
    assert 'class="processing-details"' in html


def test_result_details_uses_native_details_element():
    details = processing_details_markup()
    assert '<details class="result-details">' in details
    assert "</details>" in details


def test_result_details_is_collapsed_by_default():
    details = processing_details_markup()
    opening = details[
        details.index("<details") : details.index(">", details.index("<details")) + 1
    ]
    assert " open" not in opening


def test_processing_details_uses_native_summary_control():
    details = processing_details_markup()
    assert '<summary id="processingDetailsHeading">' in details
    assert "Processing details" in details


def test_processing_details_keeps_accessible_label_contract():
    html = read_index()
    assert 'aria-labelledby="processingDetailsHeading"' in html
    assert 'id="processingDetailsHeading"' in html


def test_processing_details_has_product_safe_description():
    details = processing_details_markup()
    assert "Technical information about this summary." in details


def test_strategy_metadata_id_is_preserved():
    assert 'id="strategyValue"' in processing_details_markup()


def test_chunk_count_metadata_id_is_preserved():
    assert 'id="chunkCountValue"' in processing_details_markup()


def test_intelligence_metadata_id_is_preserved():
    assert 'id="intelligenceModeValue"' in processing_details_markup()


def test_observability_metadata_id_is_preserved():
    assert 'id="observabilityStatusValue"' in processing_details_markup()


def test_only_existing_product_safe_metadata_fields_are_present():
    details = processing_details_markup()
    expected_ids = {
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    }
    for metadata_id in expected_ids:
        assert f'id="{metadata_id}"' in details

    forbidden = (
        "api_key",
        "API key",
        "base_url",
        "Base URL",
        "prompt",
        "environment",
        "stack trace",
        "provider config",
    )
    for value in forbidden:
        assert value not in details


def test_existing_javascript_metadata_bindings_remain_compatible():
    js = read_app_js()

    for metadata_id in (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    ):
        assert f'"{metadata_id}"' in js
        assert metadata_id in js


def test_m6_result_actions_remain_present():
    html = read_index()
    assert 'id="copySummaryButton"' in html
    assert 'id="downloadSummaryButton"' in html
    assert 'id="regenerateSummaryButton"' in html


def test_m6_5_introduces_no_new_frontend_endpoint():
    js = read_app_js()
    assert "/api/v1/result-details" not in js
    assert "/api/v1/details" not in js


def test_processing_details_does_not_require_custom_javascript_toggle():
    js = read_app_js()
    assert 'getElementById("resultDetails")' not in js
    assert 'querySelector(".result-details")' not in js
