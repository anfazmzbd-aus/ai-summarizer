"""V13 M8.7 accessibility and product regression certification.

M8.7 is the combined certification boundary for the product-hardening work
completed in M8.1 through M8.6.

It does not add product functionality.

Certification scope:
- M6 feature-freeze preservation
- accessibility structure and focus continuity
- status/error/live-region continuity
- responsive product behavior
- edge-case recovery
- result-workspace accessibility
- malformed-success-response protection
- canonical summarize path preservation
- file extraction remains preprocessing-only
- approved model selection remains server-controlled
- copy/download/regenerate workflow continuity
- no persistence/history expansion
- no frontend provider credentials
- deterministic/offline regression boundary
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


def extraction_block(
    js: str,
) -> str:
    return block_between(
        js,
        "async function extractFile(",
        "function handleSelectedFiles(",
    )


# ---------------------------------------------------------------------------
# Certification source inventory
# ---------------------------------------------------------------------------


def test_m8_7_required_product_sources_exist():
    assert INDEX_HTML_PATH.is_file()
    assert APP_JS_PATH.is_file()
    assert STYLE_CSS_PATH.is_file()


@pytest.mark.parametrize(
    "test_name",
    (
        "test_v13_m8_1_accessibility_hardening_baseline.py",
        "test_v13_m8_2_keyboard_focus_hardening.py",
        "test_v13_m8_3_screen_reader_live_region_hardening.py",
        "test_v13_m8_4_responsive_small_screen_hardening.py",
        "test_v13_m8_5_error_edge_case_ux_hardening.py",
        "test_v13_m8_6_result_workspace_accessibility_hardening.py",
    ),
)
def test_all_prior_m8_certification_modules_exist(
    test_name,
):
    path = PROJECT_ROOT / "app" / "tests" / "frontend" / test_name

    assert path.is_file()


# ---------------------------------------------------------------------------
# Feature-freeze continuity
# ---------------------------------------------------------------------------


def test_single_summary_form_is_preserved():
    html = read_html()

    assert html.count('id="summaryForm"') == 1


def test_single_source_input_is_preserved():
    html = read_html()

    assert html.count('id="inputText"') == 1


def test_single_result_workspace_is_preserved():
    html = read_html()

    assert html.count('id="result"') == 1


def test_single_summary_target_is_preserved():
    html = read_html()

    assert html.count('id="summaryText"') == 1


@pytest.mark.parametrize(
    "control_id",
    (
        "summaryType",
        "summaryLength",
        "modelSelection",
        "customInstructions",
        "summarizeButton",
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_mvp_control_surface_is_preserved(
    document,
    control_id,
):
    find_by_id(
        document,
        control_id,
    )


# ---------------------------------------------------------------------------
# Accessibility structural certification
# ---------------------------------------------------------------------------


def test_main_result_is_labelled(
    document,
):
    result = find_by_id(
        document,
        "result",
    )

    assert result.attrs.get("aria-labelledby") == "resultHeading"


def test_result_heading_is_h2(
    document,
):
    heading = find_by_id(
        document,
        "resultHeading",
    )

    assert heading.tag == "h2"


def test_summary_focus_target_is_named_region(
    document,
):
    summary = find_by_id(
        document,
        "summaryContent",
    )

    assert summary.attrs.get("role") == "region"

    assert summary.attrs.get("aria-labelledby") == "resultHeading"


def test_summary_focus_target_is_keyboard_focusable(
    document,
):
    summary = find_by_id(
        document,
        "summaryContent",
    )

    assert summary.attrs.get("tabindex") == "0"


def test_result_actions_are_named_group(
    document,
):
    groups = find_by_class(
        document,
        "result-actions",
    )

    assert len(groups) == 1

    group = groups[0]

    assert group.attrs.get("role") == "group"

    assert group.attrs.get("aria-label") == "Summary actions"


@pytest.mark.parametrize(
    "button_id",
    (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ),
)
def test_result_actions_remain_native_buttons(
    document,
    button_id,
):
    button = find_by_id(
        document,
        button_id,
    )

    assert button.tag == "button"

    assert button.attrs.get("type") == "button"


# ---------------------------------------------------------------------------
# Live-region and error semantics certification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("element_id", "role"),
    (
        (
            "status",
            "status",
        ),
        (
            "modelSelectionStatus",
            "status",
        ),
        (
            "fileStatus",
            "status",
        ),
        (
            "copySummaryStatus",
            "status",
        ),
        (
            "resultStatus",
            "status",
        ),
        (
            "error",
            "alert",
        ),
        (
            "fileError",
            "alert",
        ),
    ),
)
def test_product_status_and_error_roles_are_preserved(
    document,
    element_id,
    role,
):
    element = find_by_id(
        document,
        element_id,
    )

    assert element.attrs.get("role") == role


@pytest.mark.parametrize(
    "element_id",
    (
        "status",
        "modelSelectionStatus",
        "fileStatus",
        "copySummaryStatus",
        "resultStatus",
    ),
)
def test_non_error_announcements_are_not_assertive(
    document,
    element_id,
):
    element = find_by_id(
        document,
        element_id,
    )

    assert element.attrs.get("aria-live") != "assertive"


def test_no_assertive_live_region_is_added():
    html = read_html()

    assert 'aria-live="assertive"' not in html


# ---------------------------------------------------------------------------
# Keyboard and focus certification
# ---------------------------------------------------------------------------


def test_success_focuses_completed_summary():
    js = read_js()

    block = submit_block(js)

    success = block.index("setUIState(UI_STATE.SUCCESS);")

    focus = block.index("summaryContent.focus();")

    assert success < focus


def test_empty_input_returns_focus_to_source():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (!normalizedText)")

    end = block.index("if (!hasAvailableModel())")

    section = block[start:end]

    assert "inputText.focus();" in section


def test_unavailable_model_returns_focus_to_model_control():
    js = read_js()

    block = submit_block(js)

    start = block.index("if (!hasAvailableModel())")

    end = block.index(
        "setUIState(",
        start,
    )

    section = block[start:end]

    assert "modelSelection.focus();" in section


def test_drop_zone_enter_and_space_are_supported():
    js = read_js()

    assert 'event.key === "Enter"' in js

    assert 'event.key === " "' in js


def test_drop_zone_keyboard_activation_prevents_default():
    js = read_js()

    keydown_start = js.index("fileDropZone.addEventListener(\n" '    "keydown"')

    drop_start = js.index(
        "fileDropZone.addEventListener(\n" '    "drop"',
        keydown_start,
    )

    block = js[keydown_start:drop_start]

    assert "event.preventDefault();" in block


# ---------------------------------------------------------------------------
# Focus-visible certification
# ---------------------------------------------------------------------------


def test_summary_focus_visible_style_is_preserved():
    css = read_css()

    assert re.search(
        r"\.summary-content:focus-visible\s*\{" r"[^}]*outline\s*:",
        css,
        re.DOTALL,
    )


def test_processing_details_focus_visible_style_is_preserved():
    css = read_css()

    assert re.search(
        r"\.result-details\s+summary:focus-visible\s*\{" r"[^}]*outline\s*:",
        css,
        re.DOTALL,
    )


def test_advanced_options_focus_visible_style_is_preserved():
    css = read_css()

    assert re.search(
        r"\.advanced-options\s+summary:focus-visible\s*\{" r"[^}]*outline\s*:",
        css,
        re.DOTALL,
    )


def test_primary_controls_have_focus_visible_rules():
    css = read_css()

    assert ":focus-visible" in css


# ---------------------------------------------------------------------------
# Native disclosure certification
# ---------------------------------------------------------------------------


def test_advanced_options_use_native_details(
    document,
):
    options = find_by_class(
        document,
        "advanced-options",
    )

    assert len(options) == 1

    assert options[0].tag == "details"


def test_processing_details_use_native_details(
    document,
):
    details = find_by_class(
        document,
        "result-details",
    )

    assert len(details) == 1

    assert details[0].tag == "details"


def test_processing_details_heading_is_native_summary(
    document,
):
    heading = find_by_id(
        document,
        "processingDetailsHeading",
    )

    assert heading.tag == "summary"


def test_no_custom_disclosure_aria_state_is_added():
    html = read_html()
    js = read_js()

    assert "aria-expanded=" not in html

    assert 'setAttribute("aria-expanded"' not in js


# ---------------------------------------------------------------------------
# Responsive certification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "breakpoint",
    (
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
        ("@media (min-width: 821px) " "and (max-width: 1040px)"),
        ("@media (min-width: 821px) " "and (max-height: 800px)"),
    ),
)
def test_certified_responsive_breakpoints_are_preserved(
    breakpoint,
):
    css = read_css()

    assert breakpoint in css


def test_workspace_collapses_on_narrow_viewport():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*820px\)"
        r".*?"
        r"\.workspace\s*\{"
        r"[^}]*grid-template-columns\s*:\s*1fr",
        css,
        re.DOTALL,
    )


def test_result_header_collapses_on_narrow_viewport():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*820px\)"
        r".*?"
        r"\.result-header\s*\{"
        r"[^}]*flex-direction\s*:\s*column",
        css,
        re.DOTALL,
    )


def test_metadata_collapses_on_narrow_viewport():
    css = read_css()

    assert re.search(
        r"@media\s*\(max-width:\s*820px\)"
        r".*?"
        r"\.metadata-grid\s*\{"
        r"[^}]*grid-template-columns\s*:\s*1fr",
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


def test_mobile_result_buttons_fill_width():
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
# Long-content resilience certification
# ---------------------------------------------------------------------------


def test_summary_preserves_newlines():
    css = read_css()

    assert re.search(
        r"\.summary-content\s+p\s*\{" r"[^}]*white-space\s*:\s*pre-wrap",
        css,
        re.DOTALL,
    )


def test_summary_breaks_long_tokens():
    css = read_css()

    assert re.search(
        r"\.summary-content\s+p\s*\{" r"[^}]*overflow-wrap\s*:\s*anywhere",
        css,
        re.DOTALL,
    )


def test_metadata_breaks_long_tokens():
    css = read_css()

    assert re.search(
        r"\.metadata-item\s+dd\s*\{" r"[^}]*overflow-wrap\s*:\s*anywhere",
        css,
        re.DOTALL,
    )


# ---------------------------------------------------------------------------
# M8.5 malformed-response certification
# ---------------------------------------------------------------------------


def test_success_response_requires_summary_string():
    js = read_js()

    block = submit_block(js)

    assert 'typeof payload.summary !== "string"' in block


def test_success_response_requires_non_blank_summary():
    js = read_js()

    block = submit_block(js)

    assert "payload.summary.trim().length === 0" in block


def test_invalid_success_response_has_product_safe_error():
    js = read_js()

    assert '"The summarization response is invalid."' in js


def test_summary_is_not_replaced_before_payload_validation():
    js = read_js()

    block = submit_block(js)

    validation = block.index('"The summarization response is invalid."')

    assignment = block.index("summaryText.textContent = payload.summary;")

    assert validation < assignment


# ---------------------------------------------------------------------------
# Previous-result preservation certification
# ---------------------------------------------------------------------------


def test_loading_does_not_clear_previous_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    loading_start = block.index("if (nextState === UI_STATE.LOADING)")

    success_start = block.index("if (nextState === UI_STATE.SUCCESS)")

    loading = block[loading_start:success_start]

    assert "summaryText.textContent =" not in loading


def test_error_does_not_clear_previous_summary():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error = block[error_start:]

    assert "summaryText.textContent =" not in error


def test_error_state_does_not_force_empty_result():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    error_start = block.index("if (nextState === UI_STATE.ERROR)")

    error = block[error_start:]

    assert "showEmptyResult();" not in error


# ---------------------------------------------------------------------------
# File extraction regression certification
# ---------------------------------------------------------------------------


def test_supported_file_types_remain_txt_and_pdf(
    document,
):
    file_input = find_by_id(
        document,
        "fileInput",
    )

    accept = file_input.attrs.get("accept", "")

    assert ".txt" in accept
    assert ".pdf" in accept
    assert "text/plain" in accept
    assert "application/pdf" in accept


def test_file_extraction_endpoint_is_preserved():
    js = read_js()

    assert '"/api/v1/files/extract"' in js


def test_file_extraction_does_not_call_summarize():
    js = read_js()

    block = extraction_block(js)

    assert "/api/v1/summarize" not in block


def test_failed_file_extraction_preserves_source():
    js = read_js()

    block = extraction_block(js)

    catch_start = block.index("catch (extractionError)")

    finally_start = block.index(
        "finally",
        catch_start,
    )

    catch_block = block[catch_start:finally_start]

    assert "inputText.value =" not in catch_block


def test_file_extraction_state_is_always_released():
    js = read_js()

    block = extraction_block(js)

    assert "finally" in block

    assert "setFileExtractionState(false);" in block


# ---------------------------------------------------------------------------
# Canonical summarization-path certification
# ---------------------------------------------------------------------------


def test_exactly_one_frontend_summarization_fetch_exists():
    js = read_js()

    assert js.count('fetch("/api/v1/summarize"') == 1


def test_regenerate_reuses_form_submission():
    js = read_js()

    block = block_between(
        js,
        "function regenerateSummary()",
        "regenerateSummaryButton.addEventListener",
    )

    assert "summaryForm.requestSubmit();" in block

    assert "fetch(" not in block


@pytest.mark.parametrize(
    "forbidden_endpoint",
    (
        "/api/v1/regenerate",
        "/api/v1/resummarize",
        "/api/v1/retry-summary",
    ),
)
def test_no_alternate_summary_endpoint_exists(
    forbidden_endpoint,
):
    js = read_js()

    assert forbidden_endpoint not in js


# ---------------------------------------------------------------------------
# Approved-model boundary certification
# ---------------------------------------------------------------------------


def test_product_config_endpoint_is_preserved():
    js = read_js()

    assert '"/api/v1/product-config"' in js


def test_frontend_submits_public_product_model():
    js = read_js()

    assert "product_model: modelSelection.value" in js


def test_frontend_does_not_submit_runtime_model_selection():
    html = read_html()

    assert 'name="provider"' not in html

    assert 'name="runtime_model"' not in html


def test_frontend_has_no_api_key_input():
    html = read_html().lower()

    assert "api_key" not in html

    assert "apikey" not in html


# ---------------------------------------------------------------------------
# Copy/download/regenerate continuity
# ---------------------------------------------------------------------------


def test_copy_is_client_side():
    js = read_js()

    block = block_between(
        js,
        "async function copySummary()",
        "copySummaryButton.addEventListener",
    )

    assert "navigator.clipboard.writeText" in block

    assert "fetch(" not in block


def test_download_is_client_side():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "new Blob(" in block

    assert "URL.createObjectURL" in block

    assert "fetch(" not in block


def test_download_cleans_up_object_url():
    js = read_js()

    block = block_between(
        js,
        "function downloadSummary()",
        "downloadSummaryButton.addEventListener",
    )

    assert "URL.revokeObjectURL(objectUrl);" in block


def test_result_action_eligibility_is_recalculated_after_state_changes():
    js = read_js()

    block = block_between(
        js,
        "function setUIState(",
        "function setModelState(",
    )

    assert "updateResultActionEligibility();" in block


# ---------------------------------------------------------------------------
# Safe rendering certification
# ---------------------------------------------------------------------------


def test_summary_uses_text_content():
    js = read_js()

    assert "summaryText.textContent = payload.summary;" in js


@pytest.mark.parametrize(
    "target",
    (
        "summaryText",
        "strategyValue",
        "chunkCountValue",
        "intelligenceModeValue",
        "observabilityStatusValue",
        "error",
        "fileError",
        "copySummaryStatus",
    ),
)
def test_product_dynamic_targets_do_not_use_inner_html(
    target,
):
    js = read_js()

    assert f"{target}.innerHTML" not in js


def test_dynamic_product_code_does_not_use_insert_adjacent_html():
    js = read_js()

    assert "insertAdjacentHTML" not in js


# ---------------------------------------------------------------------------
# No persistence/history expansion
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "forbidden",
    (
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.cookie",
    ),
)
def test_frontend_has_no_new_browser_persistence(
    forbidden,
):
    js = read_js()

    assert forbidden not in js


def test_frontend_has_no_history_api():
    js = read_js()

    assert "/history" not in js

    assert "/summaries" not in js


# ---------------------------------------------------------------------------
# Reduced-motion continuity
# ---------------------------------------------------------------------------


def test_reduced_motion_contract_is_preserved():
    css = read_css()

    assert "@media (prefers-reduced-motion: reduce)" in css

    assert "animation-duration: 0.01ms" in css

    assert "transition-duration: 0.01ms" in css


# ---------------------------------------------------------------------------
# Product initialization continuity
# ---------------------------------------------------------------------------


def test_initial_input_state_is_computed():
    js = read_js()

    assert "updateInputState();" in js


def test_initial_instruction_count_is_computed():
    js = read_js()

    assert "updateInstructionsCount();" in js


def test_initial_ui_state_is_idle():
    js = read_js()

    assert "setUIState(UI_STATE.IDLE);" in js


def test_product_models_load_after_ui_initialization():
    js = read_js()

    idle = js.rindex("setUIState(UI_STATE.IDLE);")

    models = js.rindex("loadProductModels();")

    assert models > idle


# ---------------------------------------------------------------------------
# M8.7 scope guardrails
# ---------------------------------------------------------------------------


def test_no_mobile_specific_duplicate_summary_form():
    html = read_html()

    assert html.count('id="summaryForm"') == 1


def test_no_duplicate_result_action_controls():
    html = read_html()

    for element_id in (
        "copySummaryButton",
        "downloadSummaryButton",
        "regenerateSummaryButton",
    ):
        assert html.count(f'id="{element_id}"') == 1


def test_m8_7_has_no_live_marker():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "pytest.mark." + "live" not in source


def test_m8_7_requires_no_provider_credentials():
    source = Path(__file__).read_text(encoding="utf-8")

    forbidden = (
        "OPENAI" + "_API_KEY",
        "OPENROUTER" + "_API_KEY",
    )

    for value in forbidden:
        assert value not in source


def test_m8_7_is_frontend_certification_scoped():
    assert (
        INDEX_HTML_PATH.relative_to(PROJECT_ROOT).as_posix()
        == "app/templates/index.html"
    )

    assert APP_JS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/app.js"

    assert STYLE_CSS_PATH.relative_to(PROJECT_ROOT).as_posix() == "static/style.css"
