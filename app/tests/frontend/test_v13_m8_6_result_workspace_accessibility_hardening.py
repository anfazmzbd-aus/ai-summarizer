"""V13 M8.6 result-workspace accessibility hardening certification.

This suite audits the completed-summary workspace independently from the
general accessibility baseline.

Scope:
- result heading and region semantics
- summary focus destination
- successful-result focus transfer
- result-state announcement
- copy/download/regenerate native semantics
- result-action grouping and accessible naming
- action eligibility and disabled-state behavior
- copy feedback live region
- keyboard-safe actions
- regeneration focus/result preservation
- processing-details native disclosure
- processing metadata semantics
- long-result readability
- focus-visible presentation
- responsive result-action reflow
- dynamic-content text safety
- malformed-response protection inherited from M8.5
- canonical architecture preservation

M8.6 is deterministic and offline.
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
            parts = item["text"]

            assert isinstance(
                parts,
                list,
            )

            parts.append(data)

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


def find_by_class(
    document: list[Element],
    class_name: str,
) -> list[Element]:
    return [
        element
        for element in document
        if (
            class_name
            in element.attrs.get(
                "class",
                "",
            ).split()
        )
    ]


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


def submit_block(
    js: str,
) -> str:
    return js[js.index("summaryForm.addEventListener(") :]


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------


def test_m8_6_required_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


def test_m8_6_html_is_non_empty():
    assert read_html().strip()


def test_m8_6_javascript_is_non_empty():
    assert read_js().strip()


def test_m8_6_stylesheet_is_non_empty():
    assert read_css().strip()


# ---------------------------------------------------------------------------
# Result workspace structure
# ---------------------------------------------------------------------------


def test_result_workspace_exists(
    document,
):
    result = find_by_id(
        document,
        "result",
    )

    assert "result-workspace" in class_tokens(result)


def test_result_workspace_is_initially_hidden(
    document,
):
    result = find_by_id(
        document,
        "result",
    )

    assert "hidden" in class_tokens(result)


def test_result_workspace_has_accessible_heading_reference(
    document,
):
    result = find_by_id(
        document,
        "result",
    )

    assert result.attrs.get("aria-labelledby") == "resultHeading"


def test_result_heading_exists(
    document,
):
    heading = find_by_id(
        document,
        "resultHeading",
    )

    assert heading.tag == "h2"


def test_result_heading_is_meaningful(
    document,
):
    heading = find_by_id(
        document,
        "resultHeading",
    )

    assert heading.text == "Summary"


def test_generated_result_context_is_visible(
    document,
):
    matching = find_by_class(
        document,
        "result-eyebrow",
    )

    assert len(matching) == 1

    assert matching[0].text == "Generated result"


# ---------------------------------------------------------------------------
# Summary focus destination
# ---------------------------------------------------------------------------


def test_summary_content_exists(
    document,
):
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert "summary-content" in class_tokens(content)


def test_summary_content_is_programmatically_focusable(
    document,
):
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("tabindex") == "0"


def test_summary_content_has_result_context(
    document,
):
    """Focused summary should announce useful result context."""
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("aria-labelledby") == "resultHeading"


def test_summary_content_has_region_semantics(
    document,
):
    """Programmatically focused result should expose meaningful semantics."""
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("role") == "region"


def test_summary_text_exists_inside_product_markup(
    document,
):
    summary = find_by_id(
        document,
        "summaryText",
    )

    assert summary.tag == "p"


def test_summary_content_is_not_live_region(
    document,
):
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("aria-live") in (
        None,
        "",
    )


def test_summary_content_is_not_alert(
    document,
):
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("role") != "alert"


# ---------------------------------------------------------------------------
# Successful result focus transfer
# ---------------------------------------------------------------------------


def test_success_assigns_summary_before_focus():
    js = read_js()

    block = submit_block(js)

    assignment = block.index("summaryText.textContent = payload.summary;")

    focus = block.index("summaryContent.focus();")

    assert assignment < focus


def test_success_state_is_set_before_focus():
    js = read_js()

    block = submit_block(js)

    success = block.index("setUIState(UI_STATE.SUCCESS);")

    focus = block.index("summaryContent.focus();")

    assert success < focus


def test_summary_content_receives_focus_after_success():
    js = read_js()

    block = submit_block(js)

    assert "summaryContent.focus();" in block


def test_failure_does_not_focus_result():
    js = read_js()

    block = submit_block(js)

    catch_start = block.index("catch (requestError)")

    catch_block = block[catch_start:]

    assert "summaryContent.focus();" not in catch_block


# ---------------------------------------------------------------------------
# Result-state announcement
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


def test_result_status_contains_text_ready(
    document,
):
    status = find_by_id(
        document,
        "resultStatus",
    )

    assert "Ready" in status.text


def test_result_status_indicator_is_decorative(
    document,
):
    indicators = find_by_class(
        document,
        "result-status-indicator",
    )

    assert len(indicators) == 1

    assert indicators[0].attrs.get("aria-hidden") == "true"


# ---------------------------------------------------------------------------
# Result-action group semantics
# ---------------------------------------------------------------------------


def test_result_actions_exist(
    document,
):
    groups = find_by_class(
        document,
        "result-actions",
    )

    assert len(groups) == 1


def test_result_actions_have_accessible_name(
    document,
):
    group = find_by_class(
        document,
        "result-actions",
    )[0]

    assert group.attrs.get("aria-label") == "Summary actions"


def test_result_actions_expose_group_semantics(
    document,
):
    """Named result controls should be exposed as one accessible group."""
    group = find_by_class(
        document,
        "result-actions",
    )[0]

    assert group.attrs.get("role") == "group"


# ---------------------------------------------------------------------------
# Native result-action controls
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("button_id", "label"),
    (
        (
            "copySummaryButton",
            "Copy summary",
        ),
        (
            "downloadSummaryButton",
            "Download TXT",
        ),
        (
            "regenerateSummaryButton",
            "Regenerate",
        ),
    ),
)
def test_result_action_is_native_button(
    document,
    button_id,
    label,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert button.tag == "button"

    assert button.attrs.get("type") == "button"

    assert label in button.text


@pytest.mark.parametrize(
    "button_id",
    (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_result_action_is_initially_disabled(
    document,
    button_id,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert "disabled" in button.attrs


@pytest.mark.parametrize(
    "button_id",
    (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_result_action_uses_shared_button_class(
    document,
    button_id,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert "result-action-button" in class_tokens(button)


# ---------------------------------------------------------------------------
# Result-action eligibility
# ---------------------------------------------------------------------------


def test_result_presence_is_checked_from_trimmed_text():
    js = read_js()

    block = block_between(
        js,
        "function hasSummaryResult()",
        "function updateResultActionEligibility()",
    )

    assert "summaryText.textContent.trim().length > 0" in block


def test_copy_disabled_without_summary():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "copySummaryButton.disabled = actionsDisabled;" in block


def test_download_disabled_without_summary():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "downloadSummaryButton.disabled = actionsDisabled;" in block


def test_regenerate_has_extended_guard():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "regenerateSummaryButton.disabled =" in block

    assert "fileExtractionInProgress" in block

    assert "!hasValidInput()" in block

    assert "!hasAvailableModel()" in block


def test_all_result_actions_disable_during_loading():
    js = read_js()

    block = block_between(
        js,
        "function updateResultActionEligibility()",
        "function setCopySummaryStatus(",
    )

    assert "currentState === UI_STATE.LOADING" in block


# ---------------------------------------------------------------------------
# Copy workflow accessibility
# ---------------------------------------------------------------------------


def test_copy_feedback_region_exists(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("role") == "status"


def test_copy_feedback_is_polite(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("aria-live") == "polite"


def test_copy_feedback_is_atomic(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("aria-atomic") == "true"


def test_copy_clears_stale_feedback_before_action():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert 'setCopySummaryStatus("");' in block


def test_copy_success_has_text_feedback():
    js = read_js()

    assert '"Summary copied."' in js


def test_copy_failure_has_text_feedback():
    js = read_js()

    assert '"Summary could not be copied."' in js


def test_copy_failure_does_not_move_focus():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert ".focus();" not in block


def test_copy_does_not_render_html():
    js = read_js()

    assert "copySummaryStatus.innerHTML" not in js


# ---------------------------------------------------------------------------
# Download workflow accessibility
# ---------------------------------------------------------------------------


def test_download_uses_summary_text_only():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "const summary = summaryText.textContent;" in block


def test_download_uses_plain_text_utf8():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "text/plain;charset=utf-8" in block


def test_download_uses_txt_extension():
    js = read_js()

    block = block_between(
        js,
        "function buildSummaryDownloadFileName(",
        "function downloadSummary()",
    )

    assert ".txt" in block


def test_download_link_is_not_left_in_dom():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "downloadLink.remove();" in block


def test_download_object_url_is_revoked():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "URL.revokeObjectURL(objectUrl);" in block


# ---------------------------------------------------------------------------
# Regenerate workflow accessibility
# ---------------------------------------------------------------------------


def test_regenerate_uses_native_form_submission():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "summaryForm.requestSubmit();" in block


def test_regenerate_does_not_duplicate_fetch():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "fetch(" not in block


def test_regenerate_does_not_force_focus_before_completion():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert ".focus();" not in block


def test_regenerate_preserves_previous_summary_while_loading():
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


def test_regenerate_failure_preserves_previous_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error_block = block[error_start:]

    assert "summaryText.textContent =" not in error_block


# ---------------------------------------------------------------------------
# M8.5 malformed-success-response protection
# ---------------------------------------------------------------------------


def test_result_workspace_requires_string_summary():
    js = read_js()

    block = submit_block(js)

    assert 'typeof payload.summary !== "string"' in block


def test_result_workspace_rejects_blank_summary():
    js = read_js()

    block = submit_block(js)

    assert "payload.summary.trim().length === 0" in block


def test_invalid_summary_never_replaces_previous_result():
    js = read_js()

    block = submit_block(js)

    validation = block.index('"The summarization response is invalid."')

    assignment = block.index("summaryText.textContent = payload.summary;")

    assert validation < assignment


# ---------------------------------------------------------------------------
# Processing-details disclosure
# ---------------------------------------------------------------------------


def test_processing_details_section_exists(
    document,
):
    sections = find_by_class(
        document,
        "processing-details",
    )

    assert len(sections) == 1


def test_processing_details_section_is_labelled(
    document,
):
    section = find_by_class(
        document,
        "processing-details",
    )[0]

    assert section.attrs.get("aria-labelledby") == "processingDetailsHeading"


def test_processing_details_uses_native_details(
    document,
):
    details = find_by_class(
        document,
        "result-details",
    )

    assert len(details) == 1

    assert details[0].tag == "details"


def test_processing_details_uses_native_summary(
    document,
):
    summary = find_by_id(
        document,
        "processingDetailsHeading",
    )

    assert summary.tag == "summary"


def test_processing_details_summary_has_meaningful_label(
    document,
):
    summary = find_by_id(
        document,
        "processingDetailsHeading",
    )

    assert summary.text == "Processing details"


def test_processing_details_not_open_by_default(
    document,
):
    details = find_by_class(
        document,
        "result-details",
    )[0]

    assert "open" not in details.attrs


def test_processing_details_does_not_use_custom_aria_expanded():
    html = read_html()
    js = read_js()

    assert "aria-expanded=" not in html

    assert 'setAttribute("aria-expanded"' not in js


# ---------------------------------------------------------------------------
# Processing metadata semantics
# ---------------------------------------------------------------------------


def test_metadata_uses_description_list(
    document,
):
    grids = find_by_class(
        document,
        "metadata-grid",
    )

    assert len(grids) == 1

    assert grids[0].tag == "dl"


@pytest.mark.parametrize(
    "term",
    (
        "Strategy",
        "Chunks",
        "Intelligence",
        "Observability",
    ),
)
def test_metadata_terms_are_dt_elements(
    document,
    term,
):
    matching = [
        element
        for element in document
        if (element.tag == "dt" and element.text == term)
    ]

    assert len(matching) == 1


@pytest.mark.parametrize(
    "value_id",
    (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    ),
)
def test_metadata_values_are_dd_elements(
    document,
    value_id,
):
    value = find_by_id(
        document,
        value_id,
    )

    assert value.tag == "dd"


def test_missing_metadata_uses_safe_placeholders():
    js = read_js()

    assert 'metadata.strategy || "—"' in js

    assert 'metadata.chunk_count ?? "—"' in js

    assert 'metadata.intelligence_mode || "—"' in js

    assert 'metadata.observability_status || "—"' in js


# ---------------------------------------------------------------------------
# Result text safety
# ---------------------------------------------------------------------------


def test_summary_uses_text_content():
    js = read_js()

    assert "summaryText.textContent = payload.summary;" in js


def test_summary_does_not_use_inner_html():
    js = read_js()

    assert "summaryText.innerHTML" not in js


@pytest.mark.parametrize(
    "target",
    (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    ),
)
def test_metadata_does_not_use_inner_html(
    target,
):
    js = read_js()

    assert f"{target}.innerHTML" not in js


# ---------------------------------------------------------------------------
# Result readability
# ---------------------------------------------------------------------------


def test_summary_content_has_readable_line_height():
    css = read_css()

    assert re.search(
        r"\.summary-content\s+p\s*\{" r"[^}]*line-height\s*:\s*1\.75",
        css,
        re.DOTALL,
    )


def test_summary_content_preserves_line_breaks():
    css = read_css()

    assert re.search(
        r"\.summary-content\s+p\s*\{" r"[^}]*white-space\s*:\s*pre-wrap",
        css,
        re.DOTALL,
    )


def test_summary_content_handles_long_tokens():
    css = read_css()

    assert re.search(
        r"\.summary-content\s+p\s*\{" r"[^}]*overflow-wrap\s*:\s*anywhere",
        css,
        re.DOTALL,
    )


def test_metadata_values_handle_long_tokens():
    css = read_css()

    assert re.search(
        r"\.metadata-item\s+dd\s*\{" r"[^}]*overflow-wrap\s*:\s*anywhere",
        css,
        re.DOTALL,
    )


# ---------------------------------------------------------------------------
# Result focus visibility
# ---------------------------------------------------------------------------


def test_summary_focus_has_visible_outline():
    css = read_css()

    assert ".summary-content:focus-visible" in css

    assert re.search(
        r"\.summary-content:focus-visible\s*\{" r"[^}]*outline\s*:",
        css,
        re.DOTALL,
    )


def test_processing_details_summary_has_visible_focus_style():
    """Native disclosure should have an explicit visible focus treatment."""
    css = read_css()

    assert re.search(
        r"\.result-details\s+summary:focus-visible\s*\{" r"[^}]*outline\s*:",
        css,
        re.DOTALL,
    )


# ---------------------------------------------------------------------------
# Responsive result-workspace accessibility
# ---------------------------------------------------------------------------


def test_result_header_stacks_on_narrow_viewports():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*820px\)"
        r".*?"
        r"\.result-header\s*\{"
        r"[^}]*flex-direction\s*:\s*column",
        css,
        re.DOTALL,
    )


def test_metadata_grid_stacks_on_narrow_viewports():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*820px\)"
        r".*?"
        r"\.metadata-grid\s*\{"
        r"[^}]*grid-template-columns\s*:\s*1fr",
        css,
        re.DOTALL,
    )


def test_result_actions_wrap():
    css = read_css()

    assert re.search(
        r"\.result-actions\s*\{" r"[^}]*flex-wrap\s*:\s*wrap",
        css,
        re.DOTALL,
    )


def test_result_actions_stack_on_mobile():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*520px\)"
        r".*?"
        r"\.result-actions\s*\{"
        r"[^}]*flex-direction\s*:\s*column",
        css,
        re.DOTALL,
    )


def test_result_action_buttons_fill_mobile_width():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*520px\)"
        r".*?"
        r"\.result-action-button\s*\{"
        r"[^}]*width\s*:\s*100%",
        css,
        re.DOTALL,
    )


# ---------------------------------------------------------------------------
# Result action status layout
# ---------------------------------------------------------------------------


def test_result_action_status_has_reserved_height():
    css = read_css()

    assert re.search(
        r"\.result-action-status\s*\{" r"[^}]*min-height\s*:",
        css,
        re.DOTALL,
    )


def test_result_action_status_is_not_visually_hidden(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert "hidden" not in class_tokens(status)


# ---------------------------------------------------------------------------
# Result state transitions
# ---------------------------------------------------------------------------


def test_success_state_shows_result():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    success_block = block[success_start:error_start]

    assert "showResult();" in success_block


def test_success_state_hides_progress_status():
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


def test_success_state_hides_previous_error():
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


# ---------------------------------------------------------------------------
# No duplicate result workflow
# ---------------------------------------------------------------------------


def test_only_one_result_workspace_exists():
    html = read_html()

    assert html.count('id="result"') == 1


def test_only_one_summary_text_target_exists():
    html = read_html()

    assert html.count('id="summaryText"') == 1


def test_only_one_result_heading_exists():
    html = read_html()

    assert html.count('id="resultHeading"') == 1


# ---------------------------------------------------------------------------
# Canonical workflow boundaries
# ---------------------------------------------------------------------------


def test_result_workspace_uses_single_summarization_fetch():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_copy_has_no_fetch():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "fetch(" not in block


def test_download_has_no_fetch():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "fetch(" not in block


def test_regenerate_has_no_direct_fetch():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "fetch(" not in block


# ---------------------------------------------------------------------------
# No persistence/history introduced
# ---------------------------------------------------------------------------


def test_result_workspace_does_not_use_local_storage():
    js = read_js()

    assert "localStorage" not in js


def test_result_workspace_does_not_use_session_storage():
    js = read_js()

    assert "sessionStorage" not in js


def test_result_workspace_does_not_use_indexed_db():
    js = read_js()

    assert "indexedDB" not in js


# ---------------------------------------------------------------------------
# Deterministic/offline boundary
# ---------------------------------------------------------------------------


def test_m8_6_has_no_live_pytest_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_6_requires_no_external_provider():
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden = (
        "openai" + ".com",
        "openrouter" + ".ai",
        "OPENAI" + "_API_KEY",
        "OPENROUTER" + "_API_KEY",
    )

    for value in forbidden:
        assert value not in source


def test_m8_6_is_frontend_scoped():
    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )

    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert STYLE_CSS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/style.css"
