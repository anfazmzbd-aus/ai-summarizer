"""V13 M8.3 screen-reader and live-region hardening certification.

This suite audits the frozen V13 product frontend for assistive-
technology communication quality.

Scope:
- status versus alert semantics
- polite live-region usage
- atomic announcements
- loading-state announcements
- model configuration announcements
- file extraction announcements
- copy-result announcements
- summary error announcements
- result readiness communication
- input/count announcements
- stale-message clearing
- decorative-content isolation
- accessible dynamic controls
- avoidance of assertive/status misuse
- avoidance of unnecessary focus movement
- screen-reader-safe result updates

M8.3 is deterministic and offline. It must not require a live provider.
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
    """Small deterministic parser for frontend accessibility audits."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self.elements: list[Element] = []

        self._stack: list[dict[str, object]] = []

    @staticmethod
    def normalize_attrs(
        attrs,
    ) -> dict[str, str]:
        return {key: value or "" for key, value in attrs}

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        normalized_attrs = self.normalize_attrs(attrs)

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
                attrs=self.normalize_attrs(attrs),
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


def describedby_ids(
    element: Element,
) -> list[str]:
    return [
        token
        for token in element.attrs.get(
            "aria-describedby",
            "",
        ).split()
        if token
    ]


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


def test_m8_3_required_frontend_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


def test_m8_3_html_is_non_empty():
    assert read_html().strip()


def test_m8_3_javascript_is_non_empty():
    assert read_js().strip()


def test_m8_3_stylesheet_is_non_empty():
    assert read_css().strip()


# ---------------------------------------------------------------------------
# Primary summarization status region
# ---------------------------------------------------------------------------


def test_summary_status_exists_once(
    document,
):
    status = find_by_id(
        document,
        "status",
    )

    assert status.tag == "p"


def test_summary_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "status",
    )

    assert status.attrs.get("role") == "status"


def test_summary_status_is_polite(
    document,
):
    status = find_by_id(
        document,
        "status",
    )

    assert status.attrs.get("aria-live") == "polite"


def test_summary_status_is_atomic(
    document,
):
    status = find_by_id(
        document,
        "status",
    )

    assert status.attrs.get("aria-atomic") == "true"


def test_summary_status_is_initially_hidden(
    document,
):
    status = find_by_id(
        document,
        "status",
    )

    assert "hidden" in class_tokens(status)


def test_loading_state_populates_summary_status():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert "status.textContent =" in block

    assert '"Generating summary..."' in block


def test_loading_state_reveals_summary_status():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert 'status.classList.remove("hidden");' in block


def test_summary_status_can_be_cleared():
    js = read_js()

    block = block_between(
        js,
        "function hideStatus()",
        "function hideError()",
    )

    assert 'status.textContent = "";' in block


def test_cleared_summary_status_is_hidden():
    js = read_js()

    block = block_between(
        js,
        "function hideStatus()",
        "function hideError()",
    )

    assert 'status.classList.add("hidden");' in block


# ---------------------------------------------------------------------------
# Summary error announcement
# ---------------------------------------------------------------------------


def test_summary_error_exists_once(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.tag == "p"


def test_summary_error_uses_alert_role(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.attrs.get("role") == "alert"


def test_summary_error_is_initially_hidden(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert "hidden" in class_tokens(error)


def test_summary_error_does_not_duplicate_status_role(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.attrs.get("role") != "status"


def test_summary_error_does_not_use_polite_live_attribute(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.attrs.get("aria-live") in (
        None,
        "",
    )


def test_error_state_populates_error_message():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert "error.textContent =" in block

    assert '"The summarization request failed."' in block


def test_error_state_reveals_alert():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert 'error.classList.remove("hidden");' in block


def test_summary_error_can_be_cleared():
    js = read_js()

    block = block_between(
        js,
        "function hideError()",
        "function showEmptyResult()",
    )

    assert 'error.textContent = "";' in block


def test_cleared_summary_error_is_hidden():
    js = read_js()

    block = block_between(
        js,
        "function hideError()",
        "function showEmptyResult()",
    )

    assert 'error.classList.add("hidden");' in block


# ---------------------------------------------------------------------------
# Status/error state coordination
# ---------------------------------------------------------------------------


def test_loading_state_clears_previous_error():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading_block = block[loading_start:success_start]

    assert "hideError();" in loading_block


def test_success_state_clears_loading_status():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    success_block = block[success_start:error_start]

    assert "hideStatus();" in success_block


def test_success_state_clears_previous_error():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    success_block = block[success_start:error_start]

    assert "hideError();" in success_block


def test_error_state_clears_loading_status():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error_block = block[error_start:]

    assert "hideStatus();" in error_block


def test_idle_state_clears_status_and_error():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    idle_start = block.index("if (nextState === UI_STATE.IDLE)")

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    idle_block = block[idle_start:loading_start]

    assert "hideStatus();" in idle_block

    assert "hideError();" in idle_block


# ---------------------------------------------------------------------------
# Product-model status announcements
# ---------------------------------------------------------------------------


def test_model_status_exists(
    document,
):
    status = find_by_id(
        document,
        "modelSelectionStatus",
    )

    assert status.tag == "p"


def test_model_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "modelSelectionStatus",
    )

    assert status.attrs.get("role") == "status"


def test_model_status_is_polite(
    document,
):
    status = find_by_id(
        document,
        "modelSelectionStatus",
    )

    assert status.attrs.get("aria-live") == "polite"


def test_model_status_is_atomic(
    document,
):
    status = find_by_id(
        document,
        "modelSelectionStatus",
    )

    assert status.attrs.get("aria-atomic") == "true"


def test_initial_model_status_is_meaningful(
    document,
):
    status = find_by_id(
        document,
        "modelSelectionStatus",
    )

    assert status.text == "Loading available models..."


def test_model_loading_state_has_announcement():
    js = read_js()

    assert '"Loading available models..."' in js


def test_model_ready_state_has_announcement():
    js = read_js()

    assert '"Model options are ready."' in js


def test_model_error_state_has_announcement():
    js = read_js()

    assert '"Model options are unavailable."' in js


def test_model_state_updates_existing_live_region():
    js = read_js()

    block = block_between(
        js,
        "function setModelState(",
        "function clearModelOptions()",
    )

    assert "modelSelectionStatus.textContent =" in block


def test_model_state_does_not_create_dynamic_live_region():
    js = read_js()

    block = block_between(
        js,
        "function setModelState(",
        "function clearModelOptions()",
    )

    assert 'createElement("p")' not in block

    assert 'createElement("div")' not in block


# ---------------------------------------------------------------------------
# File extraction status announcements
# ---------------------------------------------------------------------------


def test_file_status_exists(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert status.tag == "div"


def test_file_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert status.attrs.get("role") == "status"


def test_file_status_is_polite(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert status.attrs.get("aria-live") == "polite"


def test_file_status_is_atomic(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert status.attrs.get("aria-atomic") == "true"


def test_file_status_is_initially_hidden(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert "hidden" in class_tokens(status)


def test_file_status_has_dedicated_text_target(
    document,
):
    target = find_by_id(
        document,
        "fileStatusText",
    )

    assert target.tag == "span"


def test_file_status_uses_existing_text_target():
    js = read_js()

    block = block_between(
        js,
        "function showFileStatus(",
        "function clearFileStatus()",
    )

    assert "fileStatusText.textContent = message;" in block


def test_file_status_is_revealed_when_updated():
    js = read_js()

    block = block_between(
        js,
        "function showFileStatus(",
        "function clearFileStatus()",
    )

    assert 'fileStatus.classList.remove("hidden");' in block


def test_file_status_can_be_cleared():
    js = read_js()

    block = block_between(
        js,
        "function clearFileStatus()",
        "function resetFileSelection()",
    )

    assert 'fileStatusText.textContent = "";' in block


def test_cleared_file_status_is_hidden():
    js = read_js()

    block = block_between(
        js,
        "function clearFileStatus()",
        "function resetFileSelection()",
    )

    assert 'fileStatus.classList.add("hidden");' in block


def test_file_extraction_announces_processing():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert "showFileStatus(`Extracting ${file.name}...`);" in block


def test_file_extraction_announces_success_metadata():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert "showFileStatus(" in block

    assert "buildFileStatusMessage(payload.file)" in block


# ---------------------------------------------------------------------------
# File extraction error announcements
# ---------------------------------------------------------------------------


def test_file_error_exists(
    document,
):
    error = find_by_id(
        document,
        "fileError",
    )

    assert error.tag == "p"


def test_file_error_uses_alert_role(
    document,
):
    error = find_by_id(
        document,
        "fileError",
    )

    assert error.attrs.get("role") == "alert"


def test_file_error_is_initially_hidden(
    document,
):
    error = find_by_id(
        document,
        "fileError",
    )

    assert "hidden" in class_tokens(error)


def test_file_error_does_not_duplicate_status_role(
    document,
):
    error = find_by_id(
        document,
        "fileError",
    )

    assert error.attrs.get("role") != "status"


def test_file_error_uses_visible_text_message():
    js = read_js()

    block = block_between(
        js,
        "function showFileError(",
        "function showFileStatus(",
    )

    assert "fileError.textContent = message;" in block


def test_file_error_is_revealed_when_updated():
    js = read_js()

    block = block_between(
        js,
        "function showFileError(",
        "function showFileStatus(",
    )

    assert 'fileError.classList.remove("hidden");' in block


def test_file_error_can_be_cleared():
    js = read_js()

    block = block_between(
        js,
        "function hideFileError()",
        "function showFileError(",
    )

    assert 'fileError.textContent = "";' in block


def test_cleared_file_error_is_hidden():
    js = read_js()

    block = block_between(
        js,
        "function hideFileError()",
        "function showFileError(",
    )

    assert 'fileError.classList.add("hidden");' in block


def test_new_file_extraction_clears_previous_file_error():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert "hideFileError();" in block


# ---------------------------------------------------------------------------
# Copy action announcements
# ---------------------------------------------------------------------------


def test_copy_status_exists(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.tag in {
        "span",
        "p",
    }


def test_copy_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("role") == "status"


def test_copy_status_is_polite(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("aria-live") == "polite"


def test_copy_status_is_atomic(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("aria-atomic") == "true"


def test_copy_success_has_announcement():
    js = read_js()

    assert '"Summary copied."' in js


def test_copy_failure_has_announcement():
    js = read_js()

    assert '"Summary could not be copied."' in js


def test_copy_status_uses_dedicated_setter():
    js = read_js()

    block = block_between(
        js,
        "function setCopySummaryStatus(",
        "async function copySummary()",
    )

    assert "copySummaryStatus.textContent = message;" in block


def test_copy_operation_clears_previous_copy_status():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert 'setCopySummaryStatus("");' in block


def test_new_summary_clears_stale_copy_status():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    assert 'setCopySummaryStatus("");' in submit_block


# ---------------------------------------------------------------------------
# Input metrics announcements
# ---------------------------------------------------------------------------


def test_input_metrics_exist(
    document,
):
    metrics = find_by_id(
        document,
        "inputMetrics",
    )

    assert "input-metrics" in class_tokens(metrics)


def test_input_metrics_are_polite(
    document,
):
    metrics = find_by_id(
        document,
        "inputMetrics",
    )

    assert metrics.attrs.get("aria-live") == "polite"


def test_input_metrics_are_atomic(
    document,
):
    metrics = find_by_id(
        document,
        "inputMetrics",
    )

    assert metrics.attrs.get("aria-atomic") == "true"


def test_word_count_has_textual_unit(
    document,
):
    label = find_by_id(
        document,
        "wordCountLabel",
    )

    assert label.text in {
        "word",
        "words",
    }


def test_character_count_has_textual_unit(
    document,
):
    label = find_by_id(
        document,
        "characterCountLabel",
    )

    assert label.text in {
        "character",
        "characters",
    }


def test_word_count_is_updated_as_text():
    js = read_js()

    assert "wordCount.textContent = String(words);" in js


def test_character_count_is_updated_as_text():
    js = read_js()

    assert "characterCount.textContent = String(characters);" in js


def test_metric_labels_support_singular_and_plural():
    js = read_js()

    for value in (
        '"word"',
        '"words"',
        '"character"',
        '"characters"',
    ):
        assert value in js


# ---------------------------------------------------------------------------
# Custom instruction count announcement
# ---------------------------------------------------------------------------


def test_instruction_count_exists(
    document,
):
    count = find_by_id(
        document,
        "customInstructionsCount",
    )

    assert count.tag == "p"


def test_instruction_count_is_polite(
    document,
):
    count = find_by_id(
        document,
        "customInstructionsCount",
    )

    assert count.attrs.get("aria-live") == "polite"


def test_instruction_count_is_atomic(
    document,
):
    count = find_by_id(
        document,
        "customInstructionsCount",
    )

    assert count.attrs.get("aria-atomic") == "true"


def test_instruction_count_has_initial_value(
    document,
):
    count = find_by_id(
        document,
        "customInstructionsCount",
    )

    assert count.text == "0 / 2000"


def test_instruction_control_references_count(
    document,
):
    control = find_by_id(
        document,
        "customInstructions",
    )

    assert "customInstructionsCount" in describedby_ids(control)


def test_instruction_count_updates_existing_region():
    js = read_js()

    block = block_between(
        js,
        "function updateInstructionsCount()",
        "function updateMetricLabel(",
    )

    assert "customInstructionsCount.textContent =" in block


# ---------------------------------------------------------------------------
# Result readiness and result content
# ---------------------------------------------------------------------------


def test_result_status_exists(
    document,
):
    status = find_by_id(
        document,
        "resultStatus",
    )

    assert "result-status" in class_tokens(status)


def test_result_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "resultStatus",
    )

    assert status.attrs.get("role") == "status"


def test_result_status_is_polite(
    document,
):
    status = find_by_id(
        document,
        "resultStatus",
    )

    assert status.attrs.get("aria-live") == "polite"


def test_result_status_contains_textual_ready_state(
    document,
):
    status = find_by_id(
        document,
        "resultStatus",
    )

    assert "Ready" in status.text


def test_result_status_does_not_rely_only_on_color(
    document,
):
    status = find_by_id(
        document,
        "resultStatus",
    )

    assert normalize_text(status.text)


def test_result_status_indicator_is_decorative(
    document,
):
    matching = [
        element
        for element in document
        if ("result-status-indicator" in class_tokens(element))
    ]

    assert len(matching) == 1

    assert matching[0].attrs.get("aria-hidden") == "true"


def test_summary_content_is_separate_from_status_region(
    document,
):
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("role") != "status"

    assert content.attrs.get("role") != "alert"


def test_summary_text_is_written_with_text_content():
    js = read_js()

    assert "summaryText.textContent = payload.summary;" in js


def test_summary_result_does_not_use_inner_html():
    js = read_js()

    assert "summaryText.innerHTML" not in js


def test_success_reveals_result_before_focus_transfer():
    js = read_js()

    submit_block = js[js.index("summaryForm.addEventListener(") :]

    success = submit_block.index("setUIState(UI_STATE.SUCCESS);")

    focus = submit_block.index("summaryContent.focus();")

    assert success < focus


# ---------------------------------------------------------------------------
# Decorative content isolation
# ---------------------------------------------------------------------------


def test_button_spinner_is_hidden_from_assistive_technology(
    document,
):
    spinner = find_by_id(
        document,
        "buttonSpinner",
    )

    assert spinner.attrs.get("aria-hidden") == "true"


def test_brand_mark_is_hidden_from_assistive_technology(
    document,
):
    matching = [
        element for element in document if ("brand-mark" in class_tokens(element))
    ]

    assert len(matching) == 1

    assert matching[0].attrs.get("aria-hidden") == "true"


def test_metric_separator_is_hidden_from_assistive_technology(
    document,
):
    matching = [
        element for element in document if ("metric-separator" in class_tokens(element))
    ]

    assert matching

    assert all(element.attrs.get("aria-hidden") == "true" for element in matching)


def test_result_empty_icon_is_decorative(
    document,
):
    matching = [
        element
        for element in document
        if ("result-empty-icon" in class_tokens(element))
    ]

    assert len(matching) == 1

    assert matching[0].attrs.get("aria-hidden") == "true"


# ---------------------------------------------------------------------------
# Dynamic control descriptions
# ---------------------------------------------------------------------------


def test_model_selector_has_status_description(
    document,
):
    model = find_by_id(
        document,
        "modelSelection",
    )

    references = describedby_ids(model)

    assert "modelSelectionStatus" in references


def test_custom_instructions_have_help_description(
    document,
):
    control = find_by_id(
        document,
        "customInstructions",
    )

    references = describedby_ids(control)

    assert "customInstructionsHelp" in references


def test_custom_instructions_have_counter_description(
    document,
):
    control = find_by_id(
        document,
        "customInstructions",
    )

    references = describedby_ids(control)

    assert "customInstructionsCount" in references


def test_file_input_has_help_description(
    document,
):
    control = find_by_id(
        document,
        "fileInput",
    )

    assert "fileIngestionHelp" in describedby_ids(control)


def test_file_drop_zone_has_help_description(
    document,
):
    control = find_by_id(
        document,
        "fileDropZone",
    )

    assert "fileIngestionHelp" in describedby_ids(control)


def test_source_text_has_help_description(
    document,
):
    control = find_by_id(
        document,
        "inputText",
    )

    assert "inputTextHelp" in describedby_ids(control)


# ---------------------------------------------------------------------------
# Avoid conflicting live-region semantics
# ---------------------------------------------------------------------------


def test_status_regions_do_not_use_alert_role(
    document,
):
    status_ids = (
        "status",
        "fileStatus",
        "modelSelectionStatus",
        "resultStatus",
        "copySummaryStatus",
    )

    for element_id in status_ids:
        element = find_by_id(
            document,
            element_id,
        )

        assert element.attrs.get("role") != "alert"


def test_error_regions_do_not_use_status_role(
    document,
):
    for element_id in (
        "error",
        "fileError",
    ):
        element = find_by_id(
            document,
            element_id,
        )

        assert element.attrs.get("role") != "status"


def test_no_assertive_live_region_is_used(
    document,
):
    assert all(element.attrs.get("aria-live") != "assertive" for element in document)


def test_no_marquee_role_is_used(
    document,
):
    assert all(element.attrs.get("role") != "marquee" for element in document)


def test_no_log_role_is_used(
    document,
):
    assert all(element.attrs.get("role") != "log" for element in document)


def test_no_timer_role_is_used(
    document,
):
    assert all(element.attrs.get("role") != "timer" for element in document)


# ---------------------------------------------------------------------------
# Announcement focus safety
# ---------------------------------------------------------------------------


def test_show_file_error_does_not_move_focus():
    js = read_js()

    block = block_between(
        js,
        "function showFileError(",
        "function showFileStatus(",
    )

    assert ".focus();" not in block


def test_show_file_status_does_not_move_focus():
    js = read_js()

    block = block_between(
        js,
        "function showFileStatus(",
        "function clearFileStatus()",
    )

    assert ".focus();" not in block


def test_model_status_updates_do_not_move_focus():
    js = read_js()

    block = block_between(
        js,
        "function setModelState(",
        "function clearModelOptions()",
    )

    assert ".focus();" not in block


def test_copy_status_updates_do_not_move_focus():
    js = read_js()

    block = block_between(
        js,
        "function setCopySummaryStatus(",
        "async function copySummary()",
    )

    assert ".focus();" not in block


def test_ui_status_function_itself_does_not_move_focus():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert ".focus();" not in block


# ---------------------------------------------------------------------------
# Hidden-state hardening
# ---------------------------------------------------------------------------


def test_hidden_utility_exists():
    css = read_css()

    assert ".hidden" in css


def test_hidden_statuses_are_not_only_visually_transparent():
    css = read_css()

    hidden_start = css.index(".hidden")

    hidden_end = css.index(
        "}",
        hidden_start,
    )

    hidden_block = css[hidden_start:hidden_end]

    assert "opacity: 0" not in hidden_block


def test_visually_hidden_utility_is_distinct_from_hidden_utility():
    css = read_css()

    assert ".visually-hidden" in css

    assert ".hidden" in css


# ---------------------------------------------------------------------------
# Screen-reader-safe loading button
# ---------------------------------------------------------------------------


def test_loading_spinner_is_decorative(
    document,
):
    spinner = find_by_id(
        document,
        "buttonSpinner",
    )

    assert spinner.attrs.get("aria-hidden") == "true"


def test_loading_button_has_text_label_target(
    document,
):
    label = find_by_id(
        document,
        "buttonLabel",
    )

    assert label.tag == "span"


def test_loading_button_label_changes_to_text():
    js = read_js()

    block = block_between(
        js,
        "function setLoadingButton(",
        "function setUIState(",
    )

    assert '"Summarizing..."' in block

    assert '"Summarize"' in block


def test_loading_button_does_not_rely_only_on_spinner():
    js = read_js()

    block = block_between(
        js,
        "function setLoadingButton(",
        "function setUIState(",
    )

    assert "buttonLabel.textContent" in block


# ---------------------------------------------------------------------------
# Accessible processing-details disclosure
# ---------------------------------------------------------------------------


def test_processing_details_use_native_summary(
    document,
):
    summary = find_by_id(
        document,
        "processingDetailsHeading",
    )

    assert summary.tag == "summary"

    assert summary.text == "Processing details"


def test_processing_details_use_native_details(
    document,
):
    matching = [
        element
        for element in document
        if (element.tag == "details" and "result-details" in class_tokens(element))
    ]

    assert len(matching) == 1


def test_processing_disclosure_is_not_reimplemented_with_aria_expanded():
    js = read_js()

    assert 'setAttribute("aria-expanded"' not in js


# ---------------------------------------------------------------------------
# Advanced-options disclosure accessibility
# ---------------------------------------------------------------------------


def test_advanced_options_use_native_details(
    document,
):
    matching = [
        element
        for element in document
        if (element.tag == "details" and "advanced-options" in class_tokens(element))
    ]

    assert len(matching) == 1


def test_advanced_options_have_native_summary(
    document,
):
    matching = [
        element
        for element in document
        if (element.tag == "summary" and element.text == "Advanced options")
    ]

    assert len(matching) == 1


def test_advanced_options_are_not_given_redundant_live_region(
    document,
):
    details = [
        element
        for element in document
        if (element.tag == "details" and "advanced-options" in class_tokens(element))
    ][0]

    assert "aria-live" not in details.attrs


# ---------------------------------------------------------------------------
# Result preservation and announcement safety
# ---------------------------------------------------------------------------


def test_loading_state_does_not_clear_previous_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading_block = block[loading_start:success_start]

    assert "summaryText.textContent =" not in loading_block


def test_error_state_does_not_clear_previous_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error_block = block[error_start:]

    assert "summaryText.textContent =" not in error_block


def test_failed_file_extraction_does_not_clear_source_text():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    catch_start = block.index("catch (extractionError)")

    finally_start = block.index(
        "finally",
        catch_start,
    )

    catch_block = block[catch_start:finally_start]

    assert "inputText.value =" not in catch_block


# ---------------------------------------------------------------------------
# No unsafe dynamic HTML for announcements
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "target",
    (
        "status",
        "error",
        "fileStatusText",
        "fileError",
        "modelSelectionStatus",
        "copySummaryStatus",
    ),
)
def test_dynamic_announcement_targets_do_not_use_inner_html(
    target,
):
    js = read_js()

    assert f"{target}.innerHTML" not in js


@pytest.mark.parametrize(
    "target",
    (
        "status",
        "error",
        "fileStatusText",
        "fileError",
        "modelSelectionStatus",
        "copySummaryStatus",
    ),
)
def test_dynamic_announcement_targets_do_not_use_insert_adjacent_html(
    target,
):
    js = read_js()

    assert f"{target}.insertAdjacentHTML" not in js


# ---------------------------------------------------------------------------
# No redundant live-region creation
# ---------------------------------------------------------------------------


def test_javascript_does_not_create_role_status_elements_dynamically():
    js = read_js()

    assert 'setAttribute("role", "status")' not in js

    assert "setAttribute('role', 'status')" not in js


def test_javascript_does_not_create_role_alert_elements_dynamically():
    js = read_js()

    assert 'setAttribute("role", "alert")' not in js

    assert "setAttribute('role', 'alert')" not in js


def test_javascript_does_not_create_assertive_live_regions():
    js = read_js()

    assert '"aria-live", "assertive"' not in js

    assert "'aria-live', 'assertive'" not in js


# ---------------------------------------------------------------------------
# Screen-reader architecture boundaries
# ---------------------------------------------------------------------------


def test_m8_3_does_not_add_second_summarization_path():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_file_extraction_remains_preprocessing_only():
    js = read_js()

    block = block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )

    assert "/api/v1/summarize" not in block


def test_regenerate_remains_canonical_form_submission():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "summaryForm.requestSubmit();" in block

    assert "fetch(" not in block


def test_m8_3_has_no_live_pytest_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_3_requires_no_external_provider():
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden = (
        "openai" + ".com",
        "openrouter" + ".ai",
        "OPENAI" + "_API_KEY",
        "OPENROUTER" + "_API_KEY",
    )

    for value in forbidden:
        assert value not in source


def test_m8_3_is_frontend_scoped():
    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )

    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert STYLE_CSS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/style.css"
