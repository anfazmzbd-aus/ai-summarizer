from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_PATH = ROOT / "app" / "templates" / "index.html"
SCRIPT_PATH = ROOT / "static" / "app.js"


def read_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_download_txt_control_is_present() -> None:
    template = read_template()
    assert 'id="downloadSummaryButton"' in template
    assert "Download TXT" in template


def test_download_control_is_a_non_submit_button() -> None:
    template = read_template()
    start = template.index('id="downloadSummaryButton"')
    control = template[start : start + 300]
    assert 'type="button"' in control


def test_download_is_disabled_before_success() -> None:
    template = read_template()
    start = template.index('id="downloadSummaryButton"')
    control = template[start : start + 300]
    assert "disabled" in control


def test_download_uses_rendered_summary_only() -> None:
    script = read_script()
    start = script.index("function downloadSummary()")
    end = script.index(
        "downloadSummaryButton.addEventListener",
        start,
    )
    logic = script[start:end]
    assert "summaryText.textContent" in logic
    assert "inputText.value" not in logic
    assert "metadata" not in logic
    assert "customInstructions" not in logic
    assert "strategyValue" not in logic
    assert "product_model" not in logic


def test_download_is_utf8_plain_text() -> None:
    script = read_script()
    assert "new Blob(" in script
    assert "[summary]" in script
    assert 'type: "text/plain;charset=utf-8"' in script


def test_download_filename_uses_required_prefix_and_extension() -> None:
    script = read_script()
    assert "function buildSummaryDownloadFileName(" in script
    assert "`ai-summary-${day}-${month}-${year}-`" in script
    assert "`${hours}${minutes}${seconds}.txt`" in script


def test_download_filename_uses_browser_local_date_components() -> None:
    script = read_script()
    start = script.index("function buildSummaryDownloadFileName(")
    end = script.index("function downloadSummary()", start)
    logic = script[start:end]
    assert "date.getDate()" in logic
    assert "date.getMonth() + 1" in logic
    assert "date.getFullYear()" in logic
    assert "date.getHours()" in logic
    assert "date.getMinutes()" in logic
    assert "date.getSeconds()" in logic
    assert "getUTC" not in logic


def test_download_filename_zero_pads_timestamp_parts() -> None:
    script = read_script()
    assert "function padTimestampPart(value)" in script
    assert 'String(value).padStart(2, "0")' in script
    assert "padTimestampPart(date.getDate())" in script
    assert "padTimestampPart(date.getMonth() + 1)" in script
    assert "padTimestampPart(date.getHours())" in script
    assert "padTimestampPart(date.getMinutes())" in script
    assert "padTimestampPart(date.getSeconds())" in script


def test_download_uses_browser_object_url_lifecycle() -> None:
    script = read_script()
    start = script.index("function downloadSummary()")
    end = script.index(
        "downloadSummaryButton.addEventListener",
        start,
    )
    logic = script[start:end]
    assert "URL.createObjectURL(blob)" in logic
    assert 'document.createElement("a")' in logic
    assert "downloadLink.click()" in logic
    assert "downloadLink.remove()" in logic
    assert "URL.revokeObjectURL(objectUrl)" in logic


def test_download_requires_a_successful_summary() -> None:
    script = read_script()
    start = script.index("function downloadSummary()")
    end = script.index(
        "downloadSummaryButton.addEventListener",
        start,
    )
    logic = script[start:end]
    assert "!hasSummaryResult()" in logic


def test_download_is_unavailable_while_loading() -> None:
    script = read_script()
    assert "downloadSummaryButton.disabled = actionsDisabled" in script
    start = script.index("function updateResultActionEligibility()")
    end = script.index("function setCopySummaryStatus", start)
    logic = script[start:end]
    assert "currentState === UI_STATE.LOADING" in logic


def test_download_introduces_no_backend_export_endpoint() -> None:
    script = read_script()
    assert "/api/v1/download" not in script
    assert "/api/v1/export" not in script
    assert "/api/v1/results/download" not in script
    assert script.count('fetch("/api/v1/summarize"') == 1


def test_download_preserves_copy_summary_action() -> None:
    template = read_template()
    script = read_script()
    assert 'id="copySummaryButton"' in template
    assert "navigator.clipboard.writeText(" in script
    assert "copySummaryButton.addEventListener" in script


def test_download_preserves_canonical_summarization_request() -> None:
    script = read_script()
    assert 'fetch("/api/v1/summarize"' in script
    assert "product_model: modelSelection.value" in script
    assert "summary_type: summaryType.value" in script
    assert "summary_length: summaryLength.value" in script
    assert "instructions: customInstructions.value.trim() || null" in script
