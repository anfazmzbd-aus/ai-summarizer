from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "app" / "templates" / "index.html"
SCRIPT = ROOT / "static" / "app.js"


def read_template() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def read_script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_regenerate_control_is_present_and_not_a_submit_button():
    html = read_template()
    start = html.index('id="regenerateSummaryButton"')
    block = html[start : start + 260]

    assert 'type="button"' in block
    assert "Regenerate" in block
    assert "disabled" in block


def test_regenerate_control_is_part_of_summary_actions():
    html = read_template()
    actions_start = html.index('class="result-actions"')
    details_start = html.index('class="processing-details"')
    actions = html[actions_start:details_start]

    assert 'id="copySummaryButton"' in actions
    assert 'id="downloadSummaryButton"' in actions
    assert 'id="regenerateSummaryButton"' in actions


def test_regenerate_element_is_bound_in_javascript():
    script = read_script()

    assert 'document.getElementById(\n    "regenerateSummaryButton"\n)' in script
    assert (
        'regenerateSummaryButton.addEventListener(\n    "click",\n    regenerateSummary\n);'
        in script
    )


def test_regenerate_requires_an_existing_summary():
    script = read_script()
    start = script.index("function regenerateSummary()")
    end = script.index("regenerateSummaryButton.addEventListener", start)
    block = script[start:end]

    assert "!hasSummaryResult()" in block


def test_regenerate_is_blocked_during_active_summary_request():
    script = read_script()
    start = script.index("function regenerateSummary()")
    end = script.index("regenerateSummaryButton.addEventListener", start)
    block = script[start:end]

    assert "currentState === UI_STATE.LOADING" in block


def test_regenerate_is_blocked_during_file_extraction():
    script = read_script()
    start = script.index("function regenerateSummary()")
    end = script.index("regenerateSummaryButton.addEventListener", start)
    block = script[start:end]

    assert "fileExtractionInProgress" in block


def test_regenerate_requires_current_valid_source_and_model():
    script = read_script()
    start = script.index("function regenerateSummary()")
    end = script.index("regenerateSummaryButton.addEventListener", start)
    block = script[start:end]

    assert "!hasValidInput()" in block
    assert "!hasAvailableModel()" in block


def test_regenerate_reuses_existing_form_submission_path():
    script = read_script()
    start = script.index("function regenerateSummary()")
    end = script.index("regenerateSummaryButton.addEventListener", start)
    block = script[start:end]

    assert "summaryForm.requestSubmit();" in block
    assert "fetch(" not in block


def test_regenerate_does_not_introduce_an_alternate_summary_endpoint():
    script = read_script()

    assert script.count('fetch("/api/v1/summarize"') == 1
    assert "/regenerate" not in script
    assert "/api/v1/regenerate" not in script


def test_existing_submit_handler_reads_current_source_and_controls():
    script = read_script()
    start = script.index('summaryForm.addEventListener(\n    "submit"')
    block = script[start:]

    assert "const normalizedText = inputText.value.trim();" in block
    assert "product_model: modelSelection.value" in block
    assert "summary_type: summaryType.value" in block
    assert "summary_length: summaryLength.value" in block
    assert "instructions: customInstructions.value.trim() || null" in block


def test_result_actions_are_disabled_while_loading():
    script = read_script()
    start = script.index("function updateResultActionEligibility()")
    end = script.index("function setCopySummaryStatus", start)
    block = script[start:end]

    assert "currentState === UI_STATE.LOADING" in block
    assert "copySummaryButton.disabled = actionsDisabled" in block
    assert "downloadSummaryButton.disabled = actionsDisabled" in block
    assert "regenerateSummaryButton.disabled" in block


def test_regenerate_is_disabled_during_file_extraction():
    script = read_script()
    start = script.index("function updateResultActionEligibility()")
    end = script.index("function setCopySummaryStatus", start)
    block = script[start:end]

    assert "actionsDisabled || fileExtractionInProgress" in block
    assert (
        "updateResultActionEligibility();"
        in script[
            script.index("function setFileExtractionState") : script.index(
                "function hideFileError"
            )
        ]
    )


def test_failed_regeneration_does_not_clear_existing_summary():
    script = read_script()
    submit_start = script.index('summaryForm.addEventListener(\n    "submit"')
    submit_block = script[submit_start:]
    catch_start = submit_block.index("} catch (requestError) {")
    catch_block = submit_block[catch_start:]

    assert 'summaryText.textContent = ""' not in catch_block
    assert "showEmptyResult();" not in catch_block
    assert "setUIState(UI_STATE.ERROR, message);" in catch_block


def test_successful_regeneration_replaces_summary_through_existing_success_path():
    script = read_script()
    submit_start = script.index('summaryForm.addEventListener(\n    "submit"')
    submit_block = script[submit_start:]

    assert "summaryText.textContent = payload.summary;" in submit_block
    assert "setUIState(UI_STATE.SUCCESS);" in submit_block


def test_copy_and_download_workflows_remain_present():
    script = read_script()

    assert "async function copySummary()" in script
    assert "function downloadSummary()" in script
    assert "buildSummaryDownloadFileName" in script
    assert "navigator.clipboard.writeText" in script


def test_regenerate_introduces_no_backend_or_provider_logic():
    script = read_script()
    start = script.index("function regenerateSummary()")
    end = script.index("regenerateSummaryButton.addEventListener", start)
    block = script[start:end]

    forbidden = [
        "provider",
        "OPENAI",
        "api_key",
        "base_url",
        "prompt",
        "metadata",
    ]

    for value in forbidden:
        assert value not in block
