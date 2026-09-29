"""V13 M8.1 accessibility and product-hardening baseline audit.

This suite records the accessibility, keyboard, responsive, focus,
status-announcement, and defensive UX guarantees present at the frozen
V13 M7 product baseline.

M8.1 is intentionally audit-only.

It does not introduce new product functionality and does not require
production-source changes merely to increase test coverage.

The objective is to establish a deterministic baseline before the
focused M8 hardening milestones begin.
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_html() -> str:
    return read(INDEX_HTML_PATH)


def read_js() -> str:
    return read(APP_JS_PATH)


def read_css() -> str:
    return read(STYLE_CSS_PATH)


@dataclass(frozen=True)
class Element:
    tag: str
    attrs: dict[str, str]
    text: str


class DocumentParser(HTMLParser):
    """Minimal deterministic HTML parser for frontend source audits.

    HTML void elements such as ``meta`` and ``input`` never have closing
    tags and therefore must not remain on the parser stack.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self._stack: list[dict[str, object]] = []

        self.elements: list[Element] = []

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
        if not self._stack:
            return

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

            current = item

            del self._stack[index:]

            current_tag = current["tag"]

            current_attrs = current["attrs"]

            current_text = current["text"]

            assert isinstance(
                current_tag,
                str,
            )

            assert isinstance(
                current_attrs,
                dict,
            )

            assert isinstance(
                current_text,
                list,
            )

            self.elements.append(
                Element(
                    tag=current_tag,
                    attrs=current_attrs,
                    text=normalize_text("".join(current_text)),
                )
            )

            return


def normalize_text(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


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


def describedby_ids(
    element: Element,
) -> list[str]:
    return [
        value
        for value in element.attrs.get(
            "aria-describedby",
            "",
        ).split()
        if value
    ]


def label_targets(
    document: list[Element],
) -> set[str]:
    return {
        element.attrs["for"]
        for element in elements_with_tag(
            document,
            "label",
        )
        if element.attrs.get("for")
    }


# ---------------------------------------------------------------------------
# Baseline source inventory
# ---------------------------------------------------------------------------


def test_m8_1_frontend_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


def test_m8_1_html_is_non_empty():
    assert read_html().strip()


def test_m8_1_javascript_is_non_empty():
    assert read_js().strip()


def test_m8_1_stylesheet_is_non_empty():
    assert read_css().strip()


# ---------------------------------------------------------------------------
# Document semantics
# ---------------------------------------------------------------------------


def test_document_declares_english_language(
    document,
):
    html = elements_with_tag(
        document,
        "html",
    )

    assert len(html) == 1

    assert html[0].attrs.get("lang") == "en"


def test_document_has_utf8_charset(
    document,
):
    metas = elements_with_tag(
        document,
        "meta",
    )

    assert any(
        element.attrs.get(
            "charset",
            "",
        ).lower()
        == "utf-8"
        for element in metas
    )


def test_document_has_responsive_viewport(
    document,
):
    metas = elements_with_tag(
        document,
        "meta",
    )

    matching = [
        element for element in metas if (element.attrs.get("name") == "viewport")
    ]

    assert len(matching) == 1

    content = (
        matching[0]
        .attrs.get(
            "content",
            "",
        )
        .replace(
            " ",
            "",
        )
    )

    assert "width=device-width" in content

    assert "initial-scale=1.0" in content


def test_document_has_descriptive_title(
    document,
):
    titles = elements_with_tag(
        document,
        "title",
    )

    assert len(titles) == 1

    assert normalize_text(titles[0].text) == "AI Summarizer"


def test_document_has_main_landmark(
    document,
):
    main = elements_with_tag(
        document,
        "main",
    )

    assert len(main) == 1

    assert main[0].attrs.get("id") == "mainContent"


def test_document_has_exactly_one_h1(
    document,
):
    headings = elements_with_tag(
        document,
        "h1",
    )

    assert len(headings) == 1


def test_primary_heading_is_named(
    document,
):
    heading = find_by_id(
        document,
        "workspaceTitle",
    )

    assert heading.tag == "h1"
    assert heading.text


def test_source_panel_has_accessible_heading(
    document,
):
    heading = find_by_id(
        document,
        "sourceHeading",
    )

    assert heading.tag == "h2"
    assert heading.text


def test_result_heading_exists(
    document,
):
    heading = find_by_id(
        document,
        "resultHeading",
    )

    assert heading.tag == "h2"

    assert heading.text == "Summary"


def test_sections_use_heading_references(
    document,
):
    source_sections = [
        element
        for element in document
        if (
            element.tag == "section"
            and element.attrs.get("aria-labelledby") == "sourceHeading"
        )
    ]

    assert len(source_sections) == 1


def test_workspace_intro_uses_heading_reference(
    document,
):
    matching = [
        element
        for element in document
        if (
            element.tag == "section"
            and element.attrs.get("aria-labelledby") == "workspaceTitle"
        )
    ]

    assert len(matching) == 1


# ---------------------------------------------------------------------------
# Accessible names and form relationships
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "control_id",
    (
        "inputText",
        "summaryType",
        "summaryLength",
        "modelSelection",
        "customInstructions",
    ),
)
def test_primary_controls_have_explicit_labels(
    document,
    control_id,
):
    assert control_id in label_targets(document)


@pytest.mark.parametrize(
    "control_id",
    (
        "inputText",
        "summaryType",
        "summaryLength",
        "modelSelection",
        "customInstructions",
    ),
)
def test_primary_controls_exist_once(
    document,
    control_id,
):
    find_by_id(
        document,
        control_id,
    )


def test_source_text_is_required(
    document,
):
    input_text = find_by_id(
        document,
        "inputText",
    )

    assert "required" in input_text.attrs


def test_source_text_has_help_reference(
    document,
):
    input_text = find_by_id(
        document,
        "inputText",
    )

    assert "inputTextHelp" in describedby_ids(input_text)

    find_by_id(
        document,
        "inputTextHelp",
    )


def test_file_input_has_help_reference(
    document,
):
    file_input = find_by_id(
        document,
        "fileInput",
    )

    assert "fileIngestionHelp" in describedby_ids(file_input)


def test_file_help_text_exists(
    document,
):
    help_text = find_by_id(
        document,
        "fileIngestionHelp",
    )

    assert "10 MiB" in help_text.text

    assert "Extracted text replaces " "the current source text." in help_text.text


def test_file_ingestion_identifies_supported_types(
    document,
):
    heading = find_by_id(
        document,
        "fileIngestionHeading",
    )

    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    combined_text = (
        f"{heading.text} "
        f"{drop_zone.text} "
        f"{drop_zone.attrs.get('aria-label', '')}"
    )

    assert "TXT" in combined_text
    assert "PDF" in combined_text


def test_custom_instruction_limit_is_exposed(
    document,
):
    control = find_by_id(
        document,
        "customInstructions",
    )

    assert control.attrs.get("maxlength") == "2000"


# ---------------------------------------------------------------------------
# Button semantics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "button_id",
    (
        "chooseFileButton",
        "clearFileButton",
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_non_submit_action_buttons_use_button_type(
    document,
    button_id,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert button.tag == "button"

    assert button.attrs.get("type") == "button"


def test_summarize_button_exists(
    document,
):
    button = find_by_id(
        document,
        "summarizeButton",
    )

    assert button.tag == "button"


@pytest.mark.parametrize(
    "button_id",
    (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_result_actions_are_disabled_before_result(
    document,
    button_id,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert "disabled" in button.attrs


# ---------------------------------------------------------------------------
# File ingestion keyboard equivalence
# ---------------------------------------------------------------------------


def test_drop_zone_has_button_role(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert drop_zone.attrs.get("role") == "button"


def test_drop_zone_is_keyboard_focusable(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert drop_zone.attrs.get("tabindex") == "0"


def test_drop_zone_has_accessible_name(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert drop_zone.attrs.get("aria-label") == "Upload TXT or PDF file"


def test_drop_zone_references_file_help(
    document,
):
    drop_zone = find_by_id(
        document,
        "fileDropZone",
    )

    assert "fileIngestionHelp" in describedby_ids(drop_zone)


def test_drop_zone_handles_keydown():
    js = read_js()

    assert "fileDropZone.addEventListener(" in js

    assert '"keydown"' in js


def test_drop_zone_supports_enter_key():
    js = read_js()

    assert 'event.key === "Enter"' in js


def test_drop_zone_supports_space_key():
    js = read_js()

    assert 'event.key === " "' in js


def test_drop_zone_keyboard_activation_prevents_default():
    js = read_js()

    start = js.index("fileDropZone.addEventListener(\n" '    "keydown"')

    end = js.index(
        'for (const eventName of ["dragenter", "dragover"])',
        start,
    )

    block = js[start:end]

    assert "event.preventDefault();" in block


def test_drop_zone_keyboard_activation_opens_file_picker():
    js = read_js()

    start = js.index("fileDropZone.addEventListener(\n" '    "keydown"')

    end = js.index(
        'for (const eventName of ["dragenter", "dragover"])',
        start,
    )

    block = js[start:end]

    assert "fileInput.click();" in block


# ---------------------------------------------------------------------------
# Focus management
# ---------------------------------------------------------------------------


def test_result_content_is_programmatically_focusable(
    document,
):
    content = find_by_id(
        document,
        "summaryContent",
    )

    assert content.attrs.get("tabindex") == "0"


def test_success_moves_focus_to_summary():
    js = read_js()

    assert "summaryContent.focus();" in js


def test_empty_source_returns_focus_to_source():
    js = read_js()

    assert "inputText.focus();" in js


def test_unavailable_model_returns_focus_to_model_selector():
    js = read_js()

    assert "modelSelection.focus();" in js


def test_clear_file_returns_focus_to_source():
    js = read_js()

    marker = "clearFileButton.addEventListener("

    start = js.index(marker)

    end = js.index(
        "inputText.addEventListener(",
        start,
    )

    block = js[start:end]

    assert "inputText.focus();" in block


def test_no_positive_tabindex_is_used(
    document,
):
    for element in document:
        tabindex = element.attrs.get("tabindex")

        if tabindex is None:
            continue

        assert int(tabindex) <= 0


def test_no_autofocus_is_forced(
    document,
):
    assert all("autofocus" not in element.attrs for element in document)


# ---------------------------------------------------------------------------
# Status and error announcement baseline
# ---------------------------------------------------------------------------


def test_file_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert status.attrs.get("role") == "status"


def test_file_status_is_polite_live_region(
    document,
):
    status = find_by_id(
        document,
        "fileStatus",
    )

    assert status.attrs.get("aria-live") == "polite"

    assert status.attrs.get("aria-atomic") == "true"


def test_file_error_uses_alert_role(
    document,
):
    error = find_by_id(
        document,
        "fileError",
    )

    assert error.attrs.get("role") == "alert"


def test_summary_error_uses_alert_role(
    document,
):
    error = find_by_id(
        document,
        "error",
    )

    assert error.attrs.get("role") == "alert"


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


def test_copy_status_uses_status_role(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("role") == "status"


def test_copy_status_is_atomic_polite_region(
    document,
):
    status = find_by_id(
        document,
        "copySummaryStatus",
    )

    assert status.attrs.get("aria-live") == "polite"

    assert status.attrs.get("aria-atomic") == "true"


def test_model_status_exists(
    document,
):
    status = find_by_id(
        document,
        "modelSelectionStatus",
    )

    assert status.text


def test_loading_state_produces_text_status():
    js = read_js()

    assert '"Generating summary..."' in js


def test_model_loading_state_produces_text_status():
    js = read_js()

    assert '"Loading available models..."' in js


def test_model_ready_state_produces_text_status():
    js = read_js()

    assert '"Model options are ready."' in js


def test_model_error_state_produces_text_status():
    js = read_js()

    assert '"Model options are unavailable."' in js


def test_copy_success_produces_text_status():
    js = read_js()

    assert '"Summary copied."' in js


def test_copy_failure_produces_text_status():
    js = read_js()

    assert '"Summary could not be copied."' in js


# ---------------------------------------------------------------------------
# Non-color status communication
# ---------------------------------------------------------------------------


def test_result_status_contains_visible_text(
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
    matching = [
        element
        for element in document
        if ("result-status-indicator" in class_tokens(element))
    ]

    assert len(matching) == 1

    assert matching[0].attrs.get("aria-hidden") == "true"


def test_brand_mark_is_decorative(
    document,
):
    matching = [
        element for element in document if ("brand-mark" in class_tokens(element))
    ]

    assert len(matching) == 1

    assert matching[0].attrs.get("aria-hidden") == "true"


def test_metric_separator_is_decorative(
    document,
):
    matching = [
        element for element in document if ("metric-separator" in class_tokens(element))
    ]

    assert matching

    assert all(element.attrs.get("aria-hidden") == "true" for element in matching)


# ---------------------------------------------------------------------------
# Input metric accessibility
# ---------------------------------------------------------------------------


def test_input_metrics_are_announced_politely(
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


def test_word_count_has_text_label(
    document,
):
    count = find_by_id(
        document,
        "wordCount",
    )

    label = find_by_id(
        document,
        "wordCountLabel",
    )

    assert count.text == "0"

    assert label.text == "words"


def test_character_count_has_text_label(
    document,
):
    count = find_by_id(
        document,
        "characterCount",
    )

    label = find_by_id(
        document,
        "characterCountLabel",
    )

    assert count.text == "0"

    assert label.text == "characters"


def test_javascript_updates_metric_singular_plural():
    js = read_js()

    assert '"word"' in js

    assert '"words"' in js

    assert '"character"' in js

    assert '"characters"' in js


# ---------------------------------------------------------------------------
# Disabled-state and duplicate-action hardening
# ---------------------------------------------------------------------------


def test_submit_disabled_during_loading():
    js = read_js()

    assert "currentState === UI_STATE.LOADING" in js

    assert "summarizeButton.disabled" in js


def test_submit_disabled_during_file_extraction():
    js = read_js()

    assert "fileExtractionInProgress" in js

    assert "summarizeButton.disabled" in js


def test_submit_requires_valid_input():
    js = read_js()

    assert "!hasValidInput()" in js


def test_submit_requires_available_model():
    js = read_js()

    assert "!hasAvailableModel()" in js


def test_duplicate_summary_submission_is_guarded():
    js = read_js()

    submit_start = js.index("summaryForm.addEventListener(")

    submit_block = js[submit_start:]

    assert "if (currentState === UI_STATE.LOADING)" in submit_block

    assert "return;" in submit_block


def test_result_actions_disable_while_loading():
    js = read_js()

    assert "const actionsDisabled =" in js

    assert "currentState === UI_STATE.LOADING" in js


def test_regeneration_disabled_during_file_extraction():
    js = read_js()

    assert "regenerateSummaryButton.disabled" in js

    assert "fileExtractionInProgress" in js


# ---------------------------------------------------------------------------
# Error-state resilience
# ---------------------------------------------------------------------------


def test_summary_error_uses_safe_visible_message():
    js = read_js()

    assert '"The summarization request failed."' in js


def test_error_state_does_not_clear_existing_summary():
    js = read_js()

    start = js.index("if (nextState === UI_STATE.ERROR)")

    end = js.index(
        "updateSubmitEligibility();",
        start,
    )

    block = js[start:end]

    assert "summaryText.textContent =" not in block


def test_loading_state_does_not_clear_existing_summary():
    js = read_js()

    start = js.index("if (nextState === UI_STATE.LOADING)")

    end = js.index(
        "if (nextState === UI_STATE.SUCCESS)",
        start,
    )

    block = js[start:end]

    assert "summaryText.textContent =" not in block


def test_file_extraction_failure_does_not_replace_source():
    js = read_js()

    catch_marker = "catch (extractionError)"

    start = js.index(catch_marker)

    end = js.index(
        "finally",
        start,
    )

    block = js[start:end]

    assert "inputText.value =" not in block


# ---------------------------------------------------------------------------
# Focus-visible styling
# ---------------------------------------------------------------------------


def test_source_text_has_focus_visible_styling():
    css = read_css()

    assert "textarea:focus-visible" in css or "#inputText:focus-visible" in css


def test_secondary_buttons_have_focus_visible_styling():
    css = read_css()

    assert ".secondary-button:focus-visible" in css


def test_text_buttons_have_focus_visible_styling():
    css = read_css()

    assert ".text-button:focus-visible" in css


def test_file_drop_zone_has_focus_visible_styling():
    css = read_css()

    assert ".file-drop-zone:focus-visible" in css


def test_summary_content_has_focus_visible_styling():
    css = read_css()

    assert ".summary-content:focus-visible" in css


def test_focus_styling_uses_nonzero_visual_indicator():
    css = read_css()

    assert "var(--shadow-focus)" in css or "outline: 3px solid" in css


# ---------------------------------------------------------------------------
# Hidden-content accessibility utility
# ---------------------------------------------------------------------------


def test_visually_hidden_utility_exists():
    css = read_css()

    assert ".visually-hidden" in css


def test_visually_hidden_content_is_not_display_none():
    css = read_css()

    start = css.index(".visually-hidden")

    end = css.index(
        "}",
        start,
    )

    block = css[start:end]

    assert "display: none" not in block


def test_file_input_uses_visually_hidden_pattern(
    document,
):
    file_input = find_by_id(
        document,
        "fileInput",
    )

    assert "visually-hidden" in class_tokens(file_input)


# ---------------------------------------------------------------------------
# Responsive product baseline
# ---------------------------------------------------------------------------


def test_stylesheet_contains_mobile_breakpoint():
    css = read_css()

    assert "@media (max-width: 520px)" in css


def test_stylesheet_contains_tablet_desktop_transition():
    css = read_css()

    assert "@media (min-width: 821px)" in css


def test_stylesheet_contains_intermediate_width_layout():
    css = read_css()

    assert "max-width: 1040px" in css


def test_stylesheet_handles_short_desktop_viewports():
    css = read_css()

    assert "max-height: 800px" in css


def test_mobile_file_controls_stack():
    css = read_css()

    assert ".file-ingestion-heading" in css

    assert "flex-direction: column" in css


def test_mobile_secondary_button_can_fill_width():
    css = read_css()

    assert ".secondary-button" in css

    assert "width: 100%" in css


def test_mobile_result_actions_stack():
    css = read_css()

    assert ".result-actions" in css

    assert ".result-action-button" in css


def test_result_action_buttons_can_fill_mobile_width():
    css = read_css()

    assert ".result-action-button" in css

    assert "width: 100%" in css


# ---------------------------------------------------------------------------
# Text overflow and reflow hardening
# ---------------------------------------------------------------------------


def test_summary_text_preserves_source_line_breaks():
    css = read_css()

    assert "white-space: pre-wrap" in css


def test_summary_text_can_break_long_tokens():
    css = read_css()

    assert "overflow-wrap: anywhere" in css


def test_custom_instruction_area_is_resizable():
    css = read_css()

    assert "resize: vertical" in css


def test_result_actions_wrap_when_space_is_constrained():
    css = read_css()

    start = css.index(".result-actions")

    block = css[start : start + 500]

    assert "flex-wrap: wrap" in block


# ---------------------------------------------------------------------------
# Reduced-motion baseline
# ---------------------------------------------------------------------------


def test_reduced_motion_media_query_exists():
    css = read_css()

    assert "@media (prefers-reduced-motion: reduce)" in css


def test_reduced_motion_disables_smooth_scrolling():
    css = read_css()

    start = css.index("@media (prefers-reduced-motion: reduce)")

    block = css[start : start + 600]

    assert "scroll-behavior: auto" in block


def test_reduced_motion_minimizes_transition_duration():
    css = read_css()

    start = css.index("@media (prefers-reduced-motion: reduce)")

    block = css[start : start + 600]

    assert "transition-duration: 0.01ms" in block


def test_reduced_motion_minimizes_animation_duration():
    css = read_css()

    start = css.index("@media (prefers-reduced-motion: reduce)")

    block = css[start : start + 600]

    assert "animation-duration: 0.01ms" in block


def test_reduced_motion_limits_animation_iterations():
    css = read_css()

    start = css.index("@media (prefers-reduced-motion: reduce)")

    block = css[start : start + 600]

    assert "animation-iteration-count: 1" in block


# ---------------------------------------------------------------------------
# Result workspace accessibility
# ---------------------------------------------------------------------------


def test_result_workspace_references_result_heading(
    document,
):
    result = find_by_id(
        document,
        "result",
    )

    assert result.attrs.get("aria-labelledby") == "resultHeading"


def test_summary_result_text_has_dedicated_element(
    document,
):
    summary = find_by_id(
        document,
        "summaryText",
    )

    assert summary.tag == "p"


def test_processing_details_have_accessible_summary(
    document,
):
    summary = find_by_id(
        document,
        "processingDetailsHeading",
    )

    assert summary.tag == "summary"

    assert summary.text == "Processing details"


def test_processing_details_use_native_details_disclosure(
    document,
):
    details = [
        element
        for element in document
        if (element.tag == "details" and "result-details" in class_tokens(element))
    ]

    assert len(details) == 1


def test_processing_details_section_references_heading(
    document,
):
    matching = [
        element
        for element in document
        if ("processing-details" in class_tokens(element))
    ]

    assert len(matching) == 1

    assert matching[0].attrs.get("aria-labelledby") == "processingDetailsHeading"


@pytest.mark.parametrize(
    "metadata_id",
    (
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
    ),
)
def test_processing_metadata_uses_definition_values(
    document,
    metadata_id,
):
    value = find_by_id(
        document,
        metadata_id,
    )

    assert value.tag == "dd"


def test_processing_metadata_uses_definition_list(
    document,
):
    lists = elements_with_tag(
        document,
        "dl",
    )

    assert any("metadata-grid" in class_tokens(element) for element in lists)


# ---------------------------------------------------------------------------
# Result action accessibility
# ---------------------------------------------------------------------------


def test_copy_button_has_visible_text(
    document,
):
    button = find_by_id(
        document,
        "copySummaryButton",
    )

    assert button.text


def test_download_button_has_visible_text(
    document,
):
    button = find_by_id(
        document,
        "downloadSummaryButton",
    )

    assert "Download" in button.text


def test_regenerate_button_has_visible_text(
    document,
):
    button = find_by_id(
        document,
        "regenerateSummaryButton",
    )

    assert button.text == "Regenerate"


def test_copy_operation_copies_summary_only():
    js = read_js()

    assert "navigator.clipboard.writeText(" in js

    assert "summaryText.textContent" in js


def test_download_operation_uses_summary_only():
    js = read_js()

    start = js.index("function downloadSummary()")

    end = js.index(
        "downloadSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "const summary = summaryText.textContent;" in block


def test_regenerate_uses_existing_form_submission():
    js = read_js()

    assert "summaryForm.requestSubmit();" in js


# ---------------------------------------------------------------------------
# File action and state hardening
# ---------------------------------------------------------------------------


def test_file_picker_is_not_triggered_while_extracting():
    js = read_js()

    assert "if (!fileExtractionInProgress)" in js


def test_drop_is_ignored_while_extracting():
    js = read_js()

    assert "if (fileExtractionInProgress)" in js


def test_drag_default_behavior_is_prevented():
    js = read_js()

    assert "event.preventDefault();" in js


def test_drag_state_has_named_css_class():
    js = read_js()

    assert '"is-dragging"' in js


# ---------------------------------------------------------------------------
# JavaScript defensive-state baseline
# ---------------------------------------------------------------------------


def test_ui_state_machine_declares_idle():
    js = read_js()

    assert 'IDLE: "idle"' in js


def test_ui_state_machine_declares_loading():
    js = read_js()

    assert 'LOADING: "loading"' in js


def test_ui_state_machine_declares_success():
    js = read_js()

    assert 'SUCCESS: "success"' in js


def test_ui_state_machine_declares_error():
    js = read_js()

    assert 'ERROR: "error"' in js


def test_model_state_machine_has_loading_state():
    js = read_js()

    assert 'LOADING: "loading"' in js


def test_model_state_machine_has_ready_state():
    js = read_js()

    assert 'READY: "ready"' in js


def test_model_state_machine_has_error_state():
    js = read_js()

    assert 'ERROR: "error"' in js


def test_ui_state_is_exposed_as_body_data_attribute():
    js = read_js()

    assert "document.body.dataset.uiState = nextState;" in js


# ---------------------------------------------------------------------------
# Browser-provider isolation remains intact
# ---------------------------------------------------------------------------


def test_frontend_has_no_api_key_field(
    document,
):
    for element in document:
        element_id = element.attrs.get(
            "id",
            "",
        ).lower()

        element_name = element.attrs.get(
            "name",
            "",
        ).lower()

        assert "api_key" not in element_id

        assert "api_key" not in element_name


def test_frontend_does_not_build_private_model_mapping():
    js = read_js()

    forbidden = (
        "model.provider",
        "model.runtime_model",
        "model.api_key",
        "model.base_url",
    )

    for value in forbidden:
        assert value not in js


def test_frontend_still_uses_public_product_model_identifier():
    js = read_js()

    assert "product_model: modelSelection.value" in js


# ---------------------------------------------------------------------------
# Baseline audit boundaries
# ---------------------------------------------------------------------------


def test_m8_1_does_not_require_live_provider():
    source = Path(__file__).read_text(encoding="utf-8")

    code = compile(
        source,
        str(__file__),
        "exec",
        flags=0,
        dont_inherit=True,
    )

    assert code is not None


def test_m8_1_has_no_live_pytest_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_1_is_frontend_only():
    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )

    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert STYLE_CSS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/style.css"


def test_m8_1_does_not_change_product_architecture():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_m8_1_preserves_file_preprocessing_boundary():
    js = read_js()

    extraction_start = js.index("async function extractFile(")

    extraction_end = js.index(
        "function handleSelectedFiles(",
        extraction_start,
    )

    extraction = js[extraction_start:extraction_end]

    assert "/api/v1/summarize" not in extraction


def test_m8_1_preserves_canonical_regeneration():
    js = read_js()

    start = js.index("function regenerateSummary()")

    end = js.index(
        "regenerateSummaryButton.addEventListener",
        start,
    )

    block = js[start:end]

    assert "summaryForm.requestSubmit();" in block

    assert "fetch(" not in block
