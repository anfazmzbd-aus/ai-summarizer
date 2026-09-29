"""V13 M8.2 keyboard and focus hardening certification.

This suite certifies keyboard operability and focus-management behavior
for the frozen V13 product workflow.

Scope:
- native interactive semantics
- keyboard-operable file ingestion
- logical tab behavior
- focus visibility
- focus after successful file extraction
- focus after clearing a file
- focus after successful summarization
- focus handling for invalid input/model state
- focus preservation during recoverable failures
- loading-state interaction guards
- result-action keyboard semantics
- native details/summary disclosure behavior
- prevention of positive tabindex/focus traps

The suite must not introduce a second product execution path or require
a live provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INDEX_HTML_PATH = PROJECT_ROOT / "app" / "templates" / "index.html"

APP_JS_PATH = PROJECT_ROOT / "static" / "app.js"

STYLE_CSS_PATH = PROJECT_ROOT / "static" / "style.css"


HTML_VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


@dataclass(frozen=True)
class Element:
    tag: str
    attrs: dict[str, str]
    text: str


def normalize_text(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


class DocumentParser(HTMLParser):
    """Small deterministic parser for frontend source certification."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self.elements: list[Element] = []

        self._stack: list[dict[str, object]] = []

    @staticmethod
    def _normalize_attrs(
        attrs,
    ) -> dict[str, str]:
        return {key: value or "" for key, value in attrs}

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        normalized_attrs = self._normalize_attrs(attrs)

        if tag in HTML_VOID_ELEMENTS:
            self.elements.append(
                Element(
                    tag=tag,
                    attrs=normalized_attrs,
                    text="",
                )
            )
            return

        self._stack.append(
            {
                "tag": tag,
                "attrs": normalized_attrs,
                "text": [],
            }
        )

    def handle_startendtag(
        self,
        tag: str,
        attrs,
    ) -> None:
        self.elements.append(
            Element(
                tag=tag,
                attrs=self._normalize_attrs(attrs),
                text="",
            )
        )

    def handle_data(
        self,
        data: str,
    ) -> None:
        for item in self._stack:
            text_parts = item["text"]

            assert isinstance(
                text_parts,
                list,
            )

            text_parts.append(data)

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        if not self._stack:
            return

        for index in range(
            len(self._stack) - 1,
            -1,
            -1,
        ):
            item = self._stack[index]

            if item["tag"] != tag:
                continue

            del self._stack[index:]

            item_tag = item["tag"]
            item_attrs = item["attrs"]
            item_text = item["text"]

            assert isinstance(
                item_tag,
                str,
            )

            assert isinstance(
                item_attrs,
                dict,
            )

            assert isinstance(
                item_text,
                list,
            )

            self.elements.append(
                Element(
                    tag=item_tag,
                    attrs=item_attrs,
                    text=normalize_text("".join(item_text)),
                )
            )

            return


def read(
    path: Path,
) -> str:
    return path.read_text(encoding="utf-8")


def read_html() -> str:
    return read(INDEX_HTML_PATH)


def read_js() -> str:
    return read(APP_JS_PATH)


def read_css() -> str:
    return read(STYLE_CSS_PATH)


@pytest.fixture(scope="module")
def document() -> list[Element]:
    parser = DocumentParser()

    parser.feed(read_html())

    return parser.elements


def find_by_id(
    document: list[Element],
    element_id: str,
) -> Element:
    matching = [
        element for element in document if (element.attrs.get("id") == element_id)
    ]

    assert len(matching) == 1, (
        f"expected exactly one " f"#{element_id}, " f"found {len(matching)}"
    )

    return matching[0]


def elements_with_tag(
    document: list[Element],
    tag: str,
) -> list[Element]:
    return [element for element in document if element.tag == tag]


def class_tokens(
    element: Element,
) -> set[str]:
    return {
        token
        for token in element.attrs.get(
            "class",
            "",
        ).split()
        if token
    }


def block_between(
    source: str,
    start_marker: str,
    end_marker: str,
) -> str:
    start = source.index(start_marker)

    end = source.index(
        end_marker,
        start + len(start_marker),
    )

    return source[start:end]


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------


def test_m8_2_required_frontend_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


def test_m8_2_html_is_non_empty():
    assert read_html().strip()


def test_m8_2_javascript_is_non_empty():
    assert read_js().strip()


def test_m8_2_stylesheet_is_non_empty():
    assert read_css().strip()


# ---------------------------------------------------------------------------
# Native interactive semantics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "button_id",
    (
        "chooseFileButton",
        "clearFileButton",
        "summarizeButton",
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_action_controls_use_native_buttons(
    document,
    button_id,
):
    element = find_by_id(
        document,
        button_id,
    )

    assert element.tag == "button"


@pytest.mark.parametrize(
    "select_id",
    (
        "summaryType",
        "summaryLength",
        "modelSelection",
    ),
)
def test_selection_controls_use_native_selects(
    document,
    select_id,
):
    element = find_by_id(
        document,
        select_id,
    )

    assert element.tag == "select"


@pytest.mark.parametrize(
    "textarea_id",
    (
        "inputText",
        "customInstructions",
    ),
)
def test_text_entry_controls_use_native_textareas(
    document,
    textarea_id,
):
    element = find_by_id(
        document,
        textarea_id,
    )

    assert element.tag == "textarea"


def test_file_input_remains_native_file_input(
    document,
):
    element = find_by_id(
        document,
        "fileInput",
    )

    assert element.tag == "input"

    assert element.attrs.get("type") == "file"


# ---------------------------------------------------------------------------
# Tab-order safety
# ---------------------------------------------------------------------------


def test_no_positive_tabindex_exists(
    document,
):
    for element in document:
        tabindex = element.attrs.get("tabindex")

        if tabindex is None:
            continue

        assert int(tabindex) <= 0


def test_no_element_uses_tabindex_greater_than_zero_in_source():
    html = read_html()

    positive_tabindex = re.compile(
        r'tabindex\s*=\s*["\']' r"[1-9][0-9]*" r'["\']',
        re.IGNORECASE,
    )

    assert positive_tabindex.search(html) is None


def test_no_autofocus_attribute_is_used(
    document,
):
    assert all("autofocus" not in element.attrs for element in document)


def test_summary_content_is_focusable_without_positive_tabindex(
    document,
):
    element = find_by_id(
        document,
        "summaryContent",
    )

    assert element.attrs.get("tabindex") == "0"


def test_file_drop_zone_is_focusable_without_positive_tabindex(
    document,
):
    element = find_by_id(
        document,
        "fileDropZone",
    )

    assert element.attrs.get("tabindex") == "0"


# ---------------------------------------------------------------------------
# Keyboard-operable file ingestion
# ---------------------------------------------------------------------------


def test_file_drop_zone_exposes_button_semantics(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert drop_zone.attrs.get("role") == "button"


def test_file_drop_zone_has_accessible_name(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert drop_zone.attrs.get("aria-label") == "Upload TXT or PDF file"


def test_file_drop_zone_has_keyboard_handler():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "keydown"',
        'for (const eventName of ["dragenter", "dragover"])',
    )

    assert block


def test_file_drop_zone_supports_enter():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "keydown"',
        'for (const eventName of ["dragenter", "dragover"])',
    )

    assert 'event.key === "Enter"' in block


def test_file_drop_zone_supports_space():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "keydown"',
        'for (const eventName of ["dragenter", "dragover"])',
    )

    assert 'event.key === " "' in block


def test_file_drop_zone_keyboard_handler_prevents_default():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "keydown"',
        'for (const eventName of ["dragenter", "dragover"])',
    )

    assert "event.preventDefault();" in block


def test_file_drop_zone_keyboard_handler_opens_file_input():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "keydown"',
        'for (const eventName of ["dragenter", "dragover"])',
    )

    assert "fileInput.click();" in block


def test_file_drop_zone_keyboard_handler_respects_loading_state():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "keydown"',
        'for (const eventName of ["dragenter", "dragover"])',
    )

    assert "!fileExtractionInProgress" in block


def test_choose_file_button_respects_loading_state():
    js = read_js()

    block = block_between(
        js,
        "chooseFileButton.addEventListener(",
        "fileInput.addEventListener(",
    )

    assert "!fileExtractionInProgress" in block


def test_drop_handler_respects_loading_state():
    js = read_js()

    block = block_between(
        js,
        "fileDropZone.addEventListener(\n" '    "drop"',
        "clearFileButton.addEventListener(",
    )

    assert "if (fileExtractionInProgress)" in block

    assert "return;" in block


# ---------------------------------------------------------------------------
# File extraction focus management
# ---------------------------------------------------------------------------


def test_successful_file_extraction_focuses_source_text():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert "inputText.focus();" in block


def test_file_focus_occurs_after_source_replacement():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    replacement = block.index("inputText.value = payload.text;")

    focus = block.index("inputText.focus();")

    assert focus > replacement


def test_file_focus_occurs_after_input_metrics_update():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    update = block.index("updateInputState();")

    focus = block.index("inputText.focus();")

    assert focus > update


def test_clearing_file_focuses_source_text():
    js = read_js()

    block = block_between(
        js,
        "clearFileButton.addEventListener(",
        "inputText.addEventListener(",
    )

    assert "resetFileSelection();" in block

    assert "inputText.focus();" in block


def test_file_extraction_error_does_not_replace_source():
    js = read_js()

    extract_block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    catch_start = extract_block.index("catch (extractionError)")

    finally_start = extract_block.index(
        "finally",
        catch_start,
    )

    catch_block = extract_block[catch_start:finally_start]

    assert "inputText.value =" not in catch_block


def test_file_extraction_error_does_not_force_unexpected_focus():
    js = read_js()

    extract_block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    catch_start = extract_block.index("catch (extractionError)")

    finally_start = extract_block.index(
        "finally",
        catch_start,
    )

    catch_block = extract_block[catch_start:finally_start]

    assert ".focus();" not in catch_block


# ---------------------------------------------------------------------------
# Summarization focus management
# ---------------------------------------------------------------------------


def test_empty_source_submission_returns_focus_to_source():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    assert "inputText.focus();" in submit_block


def test_missing_model_submission_returns_focus_to_model():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    assert "modelSelection.focus();" in submit_block


def test_successful_summary_moves_focus_to_result():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    assert "summaryContent.focus();" in submit_block


def test_summary_focus_occurs_after_success_state():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    success = submit_block.index("setUIState(UI_STATE.SUCCESS);")

    focus = submit_block.index("summaryContent.focus();")

    assert focus > success


def test_summary_focus_occurs_after_summary_content_assignment():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    assignment = submit_block.index("summaryText.textContent = payload.summary;")

    focus = submit_block.index("summaryContent.focus();")

    assert focus > assignment


def test_summary_failure_does_not_force_focus_elsewhere():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    catch_start = submit_block.index("catch (requestError)")

    catch_block = submit_block[catch_start:]

    assert ".focus();" not in catch_block


def test_summary_failure_uses_alert_instead_of_forced_focus(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.attrs.get("role") == "alert"


# ---------------------------------------------------------------------------
# Loading-state keyboard hardening
# ---------------------------------------------------------------------------


def test_summarize_button_is_disabled_during_loading():
    js = read_js()

    block = block_between(
        js,
        "function updateSubmitEligibility()",
        "function updateInputState()",
    )

    assert "currentState === UI_STATE.LOADING" in block


def test_summarize_button_is_disabled_during_file_extraction():
    js = read_js()

    block = block_between(
        js,
        "function updateSubmitEligibility()",
        "function updateInputState()",
    )

    assert "fileExtractionInProgress" in block


def test_file_input_is_disabled_while_extracting():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    assert "fileInput.disabled = isLoading;" in block


def test_choose_file_button_is_disabled_while_extracting():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    assert "chooseFileButton.disabled = isLoading;" in block


def test_clear_file_button_is_disabled_while_extracting():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    assert "clearFileButton.disabled = isLoading;" in block


def test_drop_zone_exposes_aria_disabled_state():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    assert "fileDropZone.setAttribute(" in block

    assert '"aria-disabled"' in block


def test_drop_zone_aria_disabled_matches_loading_state():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    assert "String(isLoading)" in block


def test_result_actions_are_disabled_during_loading():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "currentState === UI_STATE.LOADING" in block


def test_regenerate_action_is_disabled_during_file_extraction():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "fileExtractionInProgress" in block


def test_duplicate_submit_guard_exists():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    assert "if (currentState === UI_STATE.LOADING)" in submit_block


# ---------------------------------------------------------------------------
# Result-action keyboard semantics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "button_id",
    (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_result_actions_are_native_keyboard_buttons(
    document,
    button_id,
):
    element = find_by_id(
        document,
        button_id,
    )

    assert element.tag == "button"

    assert element.attrs.get("type") == "button"


def test_copy_action_has_click_handler():
    js = read_js()

    assert "copySummaryButton.addEventListener(" in js


def test_download_action_has_click_handler():
    js = read_js()

    assert "downloadSummaryButton.addEventListener(" in js


def test_regenerate_action_has_click_handler():
    js = read_js()

    assert "regenerateSummaryButton.addEventListener(" in js


def test_regenerate_reuses_native_form_submission():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "summaryForm.requestSubmit();" in block


def test_regenerate_does_not_create_separate_fetch_path():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "fetch(" not in block


def test_copy_action_does_not_force_focus():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert ".focus();" not in block


def test_download_action_does_not_force_focus():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert ".focus();" not in block


def test_regenerate_action_does_not_force_focus_before_submit():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert ".focus();" not in block


# ---------------------------------------------------------------------------
# Native details/summary disclosure
# ---------------------------------------------------------------------------


def test_advanced_options_use_native_details(
    document,
):
    details = [
        element
        for element in document
        if (element.tag == "details" and "advanced-options" in class_tokens(element))
    ]

    assert len(details) == 1


def test_advanced_options_have_native_summary(
    document,
):
    summaries = [
        element
        for element in document
        if (element.tag == "summary" and element.text == "Advanced options")
    ]

    assert len(summaries) == 1


def test_processing_details_use_native_details(
    document,
):
    details = [
        element
        for element in document
        if (element.tag == "details" and "result-details" in class_tokens(element))
    ]

    assert len(details) == 1


def test_processing_details_use_native_summary(
    document,
):
    summary = find_by_id(
        document,
        "processingDetailsHeading",
    )

    assert summary.tag == "summary"

    assert summary.text == "Processing details"


def test_native_disclosures_do_not_use_custom_key_handlers():
    js = read_js()

    assert "processingDetailsHeading.addEventListener" not in js


def test_advanced_options_do_not_use_custom_key_handlers():
    js = read_js()

    assert 'querySelector(".advanced-options summary")' not in js


# ---------------------------------------------------------------------------
# Focus-visible styling
# ---------------------------------------------------------------------------


def test_primary_button_has_focus_visible_style():
    css = read_css()

    assert ".primary-button:focus-visible" in css


def test_secondary_button_has_focus_visible_style():
    css = read_css()

    assert ".secondary-button:focus-visible" in css


def test_text_button_has_focus_visible_style():
    css = read_css()

    assert ".text-button:focus-visible" in css


def test_file_drop_zone_has_focus_visible_style():
    css = read_css()

    assert ".file-drop-zone:focus-visible" in css


def test_textarea_has_focus_visible_style():
    css = read_css()

    assert "textarea:focus-visible" in css or "#inputText:focus-visible" in css


def test_summary_content_has_focus_visible_style():
    css = read_css()

    assert ".summary-content:focus-visible" in css


def test_select_controls_have_focus_style():
    css = read_css()

    assert (
        "select:focus" in css
        or "select:focus-visible" in css
        or ".form-field select:focus" in css
        or ".form-field select:focus-visible" in css
    )


def test_focus_style_uses_visible_outline_or_shadow():
    css = read_css()

    assert "var(--shadow-focus)" in css or "outline: 3px solid" in css


def test_focus_style_does_not_globally_remove_outline_without_replacement():
    css = read_css()

    dangerous_pattern = re.compile(
        r"\*:focus(?:-visible)?\s*\{" r"[^}]*outline\s*:\s*none" r"[^}]*\}",
        re.DOTALL,
    )

    assert dangerous_pattern.search(css) is None


# ---------------------------------------------------------------------------
# Hidden file input keyboard-access pattern
# ---------------------------------------------------------------------------


def test_file_input_uses_visually_hidden_pattern(
    document,
):
    file_input = find_by_id(
        document,
        "fileInput",
    )

    assert "visually-hidden" in class_tokens(file_input)


def test_visually_hidden_pattern_does_not_use_display_none():
    css = read_css()

    start = css.index(".visually-hidden")

    end = css.index(
        "}",
        start,
    )

    block = css[start:end]

    assert "display: none" not in block


def test_file_picker_has_visible_keyboard_equivalent(
    document,
):
    button = find_by_id(
        document,
        "chooseFileButton",
    )

    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert button.tag == "button"

    assert drop_zone.attrs.get("tabindex") == "0"


# ---------------------------------------------------------------------------
# Disabled controls and actionable focus
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "button_id",
    (
        "summarizeButton",
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_initially_unavailable_actions_are_disabled(
    document,
    button_id,
):
    element = find_by_id(
        document,
        button_id,
    )

    assert "disabled" in element.attrs


def test_model_selector_is_runtime_disabled_until_models_ready():
    js = read_js()

    block = block_between(
        js,
        "function setModelState(",
        "function clearModelOptions()",
    )

    assert "modelSelection.disabled = true;" in block

    assert "modelSelection.disabled = false;" in block


def test_loading_file_controls_use_native_disabled_where_possible():
    js = read_js()

    block = block_between(
        js,
        "function setFileExtractionState(",
        "function hideFileError()",
    )

    for statement in (
        "fileInput.disabled = isLoading;",
        "chooseFileButton.disabled = isLoading;",
        "clearFileButton.disabled = isLoading;",
    ):
        assert statement in block


# ---------------------------------------------------------------------------
# Focus preservation around status/error updates
# ---------------------------------------------------------------------------


def test_status_updates_do_not_steal_focus():
    js = read_js()

    for function_name, end_marker in (
        (
            "function showFileStatus(",
            "function clearFileStatus()",
        ),
        (
            "function showFileError(",
            "function showFileStatus(",
        ),
        (
            "function setCopySummaryStatus(",
            "async function copySummary()",
        ),
    ):
        block = block_between(
            js,
            function_name,
            end_marker,
        )

        assert ".focus();" not in block


def test_model_state_updates_do_not_steal_focus():
    js = read_js()

    block = block_between(
        js,
        "function setModelState(",
        "function clearModelOptions()",
    )

    assert ".focus();" not in block


def test_loading_state_does_not_steal_focus():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert ".focus();" not in block


# ---------------------------------------------------------------------------
# No focus traps / global keyboard capture
# ---------------------------------------------------------------------------


def test_document_does_not_register_global_keydown_handler():
    js = read_js()

    assert 'document.addEventListener("keydown"' not in js

    assert "document.addEventListener(\n" '    "keydown"' not in js


def test_window_does_not_register_global_keydown_handler():
    js = read_js()

    assert 'window.addEventListener("keydown"' not in js

    assert "window.addEventListener(\n" '    "keydown"' not in js


def test_escape_key_is_not_globally_suppressed():
    js = read_js()

    assert 'event.key === "Escape"' not in js or (
        'document.addEventListener("keydown"' not in js
    )


def test_tab_key_is_not_intercepted():
    js = read_js()

    assert 'event.key === "Tab"' not in js


def test_shift_tab_is_not_intercepted():
    js = read_js()

    assert "event.shiftKey" not in js


# ---------------------------------------------------------------------------
# Keyboard-safe result workflow
# ---------------------------------------------------------------------------


def test_summary_result_focus_target_contains_summary_text(
    document,
):
    result = find_by_id(
        document,
        "summaryContent",
    )

    summary = find_by_id(
        document,
        "summaryText",
    )

    assert result.tag == "div"

    assert summary.tag == "p"


def test_copy_status_is_announced_without_focus_change(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("role") == "status"

    assert status.attrs.get("aria-live") == "polite"


def test_summary_error_is_announced_without_focus_change(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.attrs.get("role") == "alert"


def test_file_error_is_announced_without_focus_change(
    document,
):
    error = find_by_id(
        document,
        "fileError",
    )

    assert error.attrs.get("role") == "alert"


# ---------------------------------------------------------------------------
# Focus-related architecture boundaries
# ---------------------------------------------------------------------------


def test_keyboard_hardening_does_not_add_second_summarize_fetch():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_regenerate_still_uses_canonical_form_path():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "summaryForm.requestSubmit();" in block


def test_file_extraction_still_does_not_summarize():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert "/api/v1/summarize" not in block


def test_file_extraction_uses_only_extraction_endpoint():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert '"/api/v1/files/extract"' in block


# ---------------------------------------------------------------------------
# M8.2 deterministic/offline certification boundary
# ---------------------------------------------------------------------------


def test_m8_2_has_no_live_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_2_requires_no_external_provider():
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden = (
        "openai" + ".com",
        "openrouter" + ".ai",
        "OPENAI" + "_API_KEY",
        "OPENROUTER" + "_API_KEY",
    )

    for value in forbidden:
        assert value not in source


def test_m8_2_is_frontend_scoped():
    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )

    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert STYLE_CSS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/style.css"
