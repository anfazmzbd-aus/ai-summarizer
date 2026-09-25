from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_PATH = ROOT / "app" / "templates" / "index.html"
SCRIPT_PATH = ROOT / "static" / "app.js"
STYLE_PATH = ROOT / "static" / "style.css"


def read_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def read_style() -> str:
    return STYLE_PATH.read_text(encoding="utf-8")


def test_copy_summary_control_is_present() -> None:
    template = read_template()
    assert 'id="copySummaryButton"' in template
    assert 'type="button"' in template
    assert "Copy summary" in template


def test_copy_summary_is_disabled_before_success() -> None:
    template = read_template()
    start = template.index('id="copySummaryButton"')
    control = template[start : start + 260]
    assert "disabled" in control


def test_copy_status_is_accessible() -> None:
    template = read_template()
    assert 'id="copySummaryStatus"' in template
    assert 'role="status"' in template
    assert 'aria-live="polite"' in template


def test_copy_uses_rendered_summary_only() -> None:
    script = read_script()
    assert "navigator.clipboard.writeText(" in script
    assert "summaryText.textContent" in script
    copy_start = script.index("async function copySummary()")
    copy_end = script.index("copySummaryButton.addEventListener", copy_start)
    copy_logic = script[copy_start:copy_end]
    assert "inputText.value" not in copy_logic
    assert "metadata" not in copy_logic
    assert "customInstructions" not in copy_logic
    assert "product_model" not in copy_logic


def test_copy_requires_a_successful_summary() -> None:
    script = read_script()
    assert "function hasSummaryResult()" in script
    assert "summaryText.textContent.trim().length > 0" in script
    assert "!hasSummaryResult()" in script


def test_copy_is_unavailable_while_loading() -> None:
    script = read_script()
    assert "currentState === UI_STATE.LOADING" in script
    assert "copySummaryButton.disabled" in script


def test_copy_reports_success_without_replacing_summary() -> None:
    script = read_script()
    assert 'setCopySummaryStatus("Summary copied.")' in script
    assert "summaryText.textContent = payload.summary" in script


def test_copy_failure_is_product_safe() -> None:
    script = read_script()
    assert '"Summary could not be copied."' in script
    copy_start = script.index("async function copySummary()")
    copy_end = script.index("copySummaryButton.addEventListener", copy_start)
    copy_logic = script[copy_start:copy_end]
    assert "copyError.message" not in copy_logic
    assert "stack" not in copy_logic


def test_new_summary_clears_previous_copy_status() -> None:
    script = read_script()
    summary_assignment = script.index("summaryText.textContent = payload.summary")
    clear_status = script.index('setCopySummaryStatus("")', summary_assignment)
    success_state = script.index("setUIState(UI_STATE.SUCCESS)", summary_assignment)
    assert summary_assignment < clear_status < success_state


def test_copy_introduces_no_backend_endpoint() -> None:
    script = read_script()
    assert "/api/v1/copy" not in script
    assert "/api/v1/results/copy" not in script
    assert script.count('fetch("/api/v1/summarize"') == 1


def test_existing_canonical_summarization_endpoint_is_preserved() -> None:
    script = read_script()
    assert 'fetch("/api/v1/summarize"' in script
    assert "product_model: modelSelection.value" in script
    assert "summary_type: summaryType.value" in script
    assert "summary_length: summaryLength.value" in script


def test_result_action_styles_are_present() -> None:
    style = read_style()
    assert ".result-actions" in style
    assert ".result-action-button" in style
    assert ".result-action-status" in style


def test_copy_button_has_mobile_layout_support() -> None:
    style = read_style()
    mobile = style.rfind("@media (max-width: 520px)")
    assert mobile >= 0
    mobile_style = style[mobile:]
    assert ".result-actions" in mobile_style
    assert ".result-action-button" in mobile_style
    assert "width: 100%" in mobile_style
