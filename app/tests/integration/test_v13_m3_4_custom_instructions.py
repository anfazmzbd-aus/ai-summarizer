"""V13 M3.4 custom instructions integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def get_resource(path: str) -> str:
    response = TestClient(app).get(path)

    assert response.status_code == 200

    return response.text.replace("\r\n", "\n")


def test_advanced_options_use_native_details() -> None:
    html = get_resource("/")

    assert '<details class="advanced-options">' in html
    assert "<summary>Advanced options</summary>" in html


def test_custom_instructions_control_exists() -> None:
    html = get_resource("/")

    assert 'id="customInstructions"' in html
    assert 'name="instructions"' in html


def test_custom_instructions_has_accessible_label() -> None:
    html = get_resource("/")

    assert 'for="customInstructions"' in html


def test_custom_instructions_is_optional() -> None:
    html = get_resource("/")

    start = html.index('id="customInstructions"')
    end = html.index("</textarea>", start)

    control = html[start:end]

    assert "required" not in control


def test_custom_instructions_has_2000_character_limit() -> None:
    html = get_resource("/")

    assert 'maxlength="2000"' in html


def test_custom_instructions_has_help_relationship() -> None:
    html = get_resource("/")

    assert (
        'aria-describedby="customInstructionsHelp ' 'customInstructionsCount"' in html
    )

    assert 'id="customInstructionsHelp"' in html
    assert 'id="customInstructionsCount"' in html


def test_instruction_counter_starts_at_zero() -> None:
    html = get_resource("/")

    assert "0 / 2000" in html


def test_instruction_counter_is_live_region() -> None:
    html = get_resource("/")

    start = html.index('id="customInstructionsCount"')
    end = html.index("</p>", start)

    counter = html[start:end]

    assert 'aria-live="polite"' in counter
    assert 'aria-atomic="true"' in counter


def test_javascript_references_custom_instructions() -> None:
    javascript = get_resource("/static/app.js")

    assert 'document.getElementById("customInstructions")' in javascript
    assert 'document.getElementById("customInstructionsCount")' in javascript


def test_javascript_updates_instruction_counter() -> None:
    javascript = get_resource("/static/app.js")

    assert "function updateInstructionsCount()" in javascript
    assert "customInstructions.value.length" in javascript
    assert "/ 2000" in javascript


def test_instruction_counter_updates_on_input() -> None:
    javascript = get_resource("/static/app.js")

    assert "customInstructions.addEventListener(" in javascript
    assert '"input"' in javascript
    assert "updateInstructionsCount" in javascript


def test_instruction_counter_is_initialized() -> None:
    javascript = get_resource("/static/app.js")

    assert "updateInstructionsCount();" in javascript


def test_advanced_options_have_focus_visible_style() -> None:
    stylesheet = get_resource("/static/style.css")

    assert ".advanced-options summary:focus-visible {" in stylesheet


def test_custom_instructions_have_focus_visible_style() -> None:
    stylesheet = get_resource("/static/style.css")

    assert ".advanced-options textarea:focus-visible {" in stylesheet


def test_custom_instructions_do_not_construct_prompts() -> None:
    javascript = get_resource("/static/app.js")

    assert "customInstructions.value" in javascript

    assert "resolve_summary_profile" not in javascript
    assert "resolve_length_instruction" not in javascript
    assert "SummarizationIntent" not in javascript
